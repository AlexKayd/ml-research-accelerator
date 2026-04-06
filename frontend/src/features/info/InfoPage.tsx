import { Box, Divider, List, ListItem, ListItemText, Typography } from '@mui/material'

const bullets = [
  {
    primary: 'Изучать каталог датасетов',
    secondary:
      'Табличные датасеты из Kaggle и UCI ML Repository с фильтрацией по источнику, формату, размеру и тегам.',
  },
  {
    primary: 'Генерировать EDA‑отчёты',
    secondary:
      'Один клик - и вы получаете полный профилированный отчёт в удобном HTML‑формате. Отчёты хранятся в вашей истории и доступны в любой момент.',
  },
  {
    primary: 'Сохранять избранное',
    secondary: 'Добавляйте датасеты в избранное, чтобы не потерять то, что пригодится в будущих проектах.',
  },
  {
    primary: 'Следить за обновлениями',
    secondary:
      'Сервис автоматически проверяет обновления в источниках. Отчёты перегенерируются автоматически, вы всегда работаете с актуальными данными.',
  },
]

export function InfoPage() {
  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', py: 3, px: 2 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Добро пожаловать в ML Research Accelerator
      </Typography>
      <Typography paragraph>
        ML Research Accelerator — это платформа, которая помогает исследователям и практикам машинного обучения быстро находить,
        анализировать и использовать табличные датасеты из открытых репозиториев.
      </Typography>
      <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
        Что вы можете здесь делать?
      </Typography>
      <List dense>
        {bullets.map((item) => (
          <ListItem key={item.primary} alignItems="flex-start">
            <ListItemText primary={item.primary} secondary={item.secondary} />
          </ListItem>
        ))}
      </List>
      <Typography sx={{ mt: 2 }} paragraph>
        <strong>Готовы начать?</strong> Войдите в аккаунт или зарегистрируйтесь, чтобы получить доступ к полному функционалу.
      </Typography>
      <Divider sx={{ my: 3 }} />
      <Typography variant="h6" color="warning.main" gutterBottom>
        Важная информация!
      </Typography>
      <Typography paragraph>
        Наш сервис работает только с табличными датасетами, поддерживая файлы форматов CSV и JSON, размером не более 100 MB. Генерация
        отчёта выполняется для конкретного файла выбранного датасета. Все сгенерированные отчёты автоматически сохраняются в вашу
        историю. При необходимости вы можете удалить любой отчёт из истории.
      </Typography>
      <Typography paragraph>
        Поскольку сервис зависит от внешних источников — Kaggle и UCI ML Repository, — мы автоматически отслеживаем изменения в них:
        обновляем метаданные датасетов и перегенерируем ваши отчёты при изменении соответствующих файлов. Рекомендуем внимательно
        следить за датами обновления отчётов, файлов и датасетов, чтобы не пропустить актуальные изменения.
      </Typography>
    </Box>
  )
}