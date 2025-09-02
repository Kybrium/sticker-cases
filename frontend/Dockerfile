FROM node:20-alpine
WORKDIR /app

# helpful for native-node modules if any
RUN apk add --no-cache python3 make g++

COPY package.json package-lock.json* pnpm-lock.yaml* yarn.lock* ./
RUN if [ -f package-lock.json ]; then npm ci; \
    elif [ -f yarn.lock ]; then yarn install; \
    elif [ -f pnpm-lock.yaml ]; then npm i -g pnpm && pnpm i; \
    else npm i; fi

COPY . /app
EXPOSE 3000