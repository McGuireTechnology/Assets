FROM node:24-bookworm-slim

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

EXPOSE 5174

CMD ["sh", "-c", "npm run build && npm run preview -- --host 0.0.0.0"]
