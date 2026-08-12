FROM golang:1.26.3-alpine

ENV GOPROXY=https://goproxy.cn,direct

RUN apk add --no-cache ca-certificates git \
    && go install github.com/air-verse/air@v1.67.4

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .

EXPOSE 8080

CMD ["air", "-c", ".air.toml"]
