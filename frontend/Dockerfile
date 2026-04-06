FROM node:20-alpine AS build

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

COPY . .

ARG VITE_USER_SERVICE_URL=http://localhost:8001
ARG VITE_EDA_SERVICE_URL=http://localhost:8003
ENV VITE_USER_SERVICE_URL=$VITE_USER_SERVICE_URL VITE_EDA_SERVICE_URL=$VITE_EDA_SERVICE_URL
RUN npm run build

FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80