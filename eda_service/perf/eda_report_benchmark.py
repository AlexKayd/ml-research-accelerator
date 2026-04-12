# py eda_service\perf\eda_report_benchmark.py --n 1000 --poll-interval 1 --deadline 900

import argparse
import asyncio
import os
import random
import statistics
import string
import time

import httpx


def env(name, default=None):
    v = os.getenv(name, default)
    if v is None or not str(v).strip():
        raise SystemExit(f"Не задано {name}")
    return str(v).strip()


def normalize_base_url(url: str) -> str:
    u = (url or "").strip().rstrip("/")
    if u.endswith("/api"):
        u = u[:-4]
    return u.rstrip("/")


def rand_login() -> str:
    suffix = "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))
    return f"bench_{suffix}"


def fmt_s(x: float) -> str:
    return f"{x:.2f} сек."


async def register_and_login(user_base_url: str, password: str, timeout_s: float) -> str:
    login = rand_login()

    async with httpx.AsyncClient(base_url=user_base_url, timeout=timeout_s) as c:
        r1 = await c.post("/api/auth/register", json={"login": login, "password": password})
        if r1.status_code >= 400:
            raise SystemExit(
                "Не удалось зарегистрировать пользователя\n"
                f"URL: {user_base_url}/api/auth/register\n"
                f"HTTP {r1.status_code}: {r1.text}"
            )

        await asyncio.sleep(0.05)

        r2 = await c.post("/api/auth/login", json={"login": login, "password": password})
        if r2.status_code >= 400:
            raise SystemExit(
                "Не удалось залогиниться пользователем\n"
                f"URL: {user_base_url}/api/auth/login\n"
                f"HTTP {r2.status_code}: {r2.text}\n"
            )

        data = r2.json()
        token = data.get("access_token")
        if not token:
            raise SystemExit(f"Неожиданный ответ login (нет access_token): {data}")
        return str(token)


async def create_users(user_base_url: str, password: str, n_users: int, timeout_s: float):
    tokens = []
    for _ in range(n_users):
        tok = await register_and_login(user_base_url, password=password, timeout_s=timeout_s)
        tokens.append(tok)
    return tokens


async def fetch_files(user_base_url: str, access_token: str, limit: int, timeout_s: float, page_size: int = 50):
    headers = {"Authorization": f"Bearer {access_token}"}
    files = []
    offset = 0

    async with httpx.AsyncClient(base_url=user_base_url, timeout=timeout_s) as c:
        while len(files) < limit:
            r = await c.get("/api/datasets", headers=headers, params={"limit": page_size, "offset": offset})
            r.raise_for_status()
            items = r.json()
            if not items:
                break

            for ds in items:
                for f in (ds.get("files") or []):
                    fid = f.get("file_id")
                    name = f.get("file_name")
                    if isinstance(fid, int) and isinstance(name, str) and name.strip():
                        files.append((int(fid), name.strip()))
                        if len(files) >= limit:
                            break
                if len(files) >= limit:
                    break

            offset += page_size

    seen = set()
    uniq = []
    for fid, name in files:
        if fid in seen:
            continue
        seen.add(fid)
        uniq.append((fid, name))
    return uniq[:limit]


async def generate_and_wait_one(
    eda_client: httpx.AsyncClient,
    access_token: str,
    file_id: int,
    file_name: str,
    poll_interval_s: float,
    deadline_s: float,
):
    headers = {"Authorization": f"Bearer {access_token}"}
    started = time.perf_counter()
    report_id = None
    last_status = None

    try:
        r = await eda_client.post("/api/reports/generate", headers=headers, json={"file_id": int(file_id)})
        r.raise_for_status()
        report_id = int(r.json()["report_id"])

        while True:
            elapsed = time.perf_counter() - started
            if elapsed > deadline_s:
                return {
                    "file_id": file_id,
                    "file_name": file_name,
                    "report_id": report_id,
                    "ok": False,
                    "status": "timeout",
                    "elapsed_s": elapsed,
                    "error": f"Таймаут: {deadline_s:.1f} сек.",
                }

            s = await eda_client.get(f"/api/reports/status/{report_id}", headers=headers)
            if s.status_code >= 400:
                return {
                    "file_id": file_id,
                    "file_name": file_name,
                    "report_id": report_id,
                    "ok": False,
                    "status": f"http_{s.status_code}",
                    "elapsed_s": elapsed,
                    "error": s.text,
                }

            jb = s.json()
            last_status = str(jb.get("status") or "")

            if last_status in {"completed", "failed", "deleting"}:
                ok = last_status == "completed"
                err = None
                if not ok:
                    err = str(jb.get("error_message") or "") or last_status
                return {
                    "file_id": file_id,
                    "file_name": file_name,
                    "report_id": report_id,
                    "ok": ok,
                    "status": last_status,
                    "elapsed_s": elapsed,
                    "error": err,
                }

            await asyncio.sleep(poll_interval_s)
    except Exception as e:
        elapsed = time.perf_counter() - started
        return {
            "file_id": file_id,
            "file_name": file_name,
            "report_id": report_id,
            "ok": False,
            "status": last_status,
            "elapsed_s": elapsed,
            "error": f"{type(e).__name__}: {e}",
        }


async def user_worker(
    eda_base_url: str,
    access_token: str,
    file_q: asyncio.Queue,
    out_q: asyncio.Queue,
    poll_interval_s: float,
    deadline_s: float,
    timeout_s: float,
    max_generate_per_minute: int,
):
    min_interval = 60.0 / float(max_generate_per_minute)
    last_generate_started_at = None

    async with httpx.AsyncClient(base_url=eda_base_url, timeout=timeout_s) as eda:
        while True:
            try:
                file_id, file_name = file_q.get_nowait()
            except asyncio.QueueEmpty:
                return

            now = time.perf_counter()
            if last_generate_started_at is not None:
                wait_s = min_interval - (now - last_generate_started_at)
                if wait_s > 0:
                    await asyncio.sleep(wait_s)
            last_generate_started_at = time.perf_counter()

            res = await generate_and_wait_one(
                eda_client=eda,
                access_token=access_token,
                file_id=file_id,
                file_name=file_name,
                poll_interval_s=poll_interval_s,
                deadline_s=deadline_s,
            )
            await out_q.put(res)
            file_q.task_done()


def summarize(results):
    ok = [r for r in results if r["ok"]]
    fail = [r for r in results if not r["ok"]]
    ok_times = [r["elapsed_s"] for r in ok]
    all_times = [r["elapsed_s"] for r in results]

    p50_ok = statistics.median(ok_times) if ok_times else None
    p95_ok = statistics.quantiles(ok_times, n=20)[-1] if len(ok_times) >= 20 else None
    avg_ok = (sum(ok_times) / len(ok_times)) if ok_times else None
    avg_all = (sum(all_times) / len(all_times)) if all_times else None
    min_ok = min(ok_times) if ok_times else None
    max_ok = max(ok_times) if ok_times else None

    failed_by_status = {}
    for r in fail:
        key = r.get("status")
        failed_by_status[key] = failed_by_status.get(key, 0) + 1

    return {
        "total": len(results),
        "ok": len(ok),
        "failed": len(fail),
        "avg_ok_s": avg_ok,
        "avg_all_s": avg_all,
        "p50_ok_s": p50_ok,
        "p95_ok_s": p95_ok,
        "min_ok_s": min_ok,
        "max_ok_s": max_ok,
        "failed_by_status": failed_by_status,
    }


async def main():
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=1000)
    p.add_argument("--poll-interval", type=float, default=1.0, help="Интервал опроса /status, сек")
    p.add_argument("--deadline", type=float, default=900.0, help="Максимальное время на 1 файл, сек")
    args = p.parse_args()

    user_base_url = normalize_base_url(env("USER_SERVICE_BASE_URL", "http://localhost:8001"))
    eda_base_url = normalize_base_url(env("EDA_SERVICE_BASE_URL", "http://localhost:8003"))

    password = os.getenv("BENCH_PASSWORD", "Passw0rd_123")
    timeout_s = 30.0

    n_users = 10
    max_generate_per_minute = 10

    tokens = await create_users(user_base_url, password=password, n_users=n_users, timeout_s=timeout_s)
    files = await fetch_files(user_base_url, access_token=tokens[0], limit=int(args.n), timeout_s=timeout_s, page_size=50)
    if not files:
        raise SystemExit("Не найдено ни одного data файла")

    file_q = asyncio.Queue()
    for item in files:
        file_q.put_nowait(item)

    out_q = asyncio.Queue()

    workers = []
    for i in range(n_users):
        workers.append(
            asyncio.create_task(
                user_worker(
                    eda_base_url=eda_base_url,
                    access_token=tokens[i],
                    file_q=file_q,
                    out_q=out_q,
                    poll_interval_s=float(args.poll_interval),
                    deadline_s=float(args.deadline),
                    timeout_s=timeout_s,
                    max_generate_per_minute=max_generate_per_minute,
                )
            )
        )

    started = time.perf_counter()
    results = []

    for _ in range(len(files)):
        r = await out_q.get()
        results.append(r)

        status = "СГЕНЕРИРОВАН" if r["ok"] else "НЕ СГЕНЕРИРОВАН"
        reason = f" (ошибка: {r['error']})" if (not r["ok"] and r.get("error")) else ""
        print(
            f"file_id={r['file_id']}, file_name={r['file_name']}, результат={status}, "
            f"время={fmt_s(float(r['elapsed_s']))}{reason}"
        )
        out_q.task_done()

    await file_q.join()
    for w in workers:
        await w

    total_elapsed = time.perf_counter() - started
    s = summarize(results)

    print("")
    print("Итоги:")
    print(f"- Обработано файлов: {s['total']}")
    print(f"- Общее время работы программы: {fmt_s(total_elapsed)}")
    print(f"- Среднее время успешной генерации: {fmt_s(float(s['avg_ok_s']))}")
    print(f"- Минимальное время успешной генерации: {fmt_s(float(s['min_ok_s']))}")
    print(f"- Максимальное время успешной генерации: {fmt_s(float(s['max_ok_s']))}")
    print(f"- Не сгенерированных отчётов (с ошибками): {s['failed']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))