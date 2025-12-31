FROM node:22-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:22-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production

RUN addgroup -g nodeuser && adduser -S nodeuser

COPY --from=builder --chown=nodeuser:nodeuser /app/.next/standalone ./
COPY --from=builder --chown=nodeuser:nodeuser /app/.next/static ./.next/static
COPY --from=builder --chown=nodeuser:nodeuser /app/public ./public

USER nodeuser

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
