FROM golang:1.18-bullseye

WORKDIR /app

COPY . .

ENV PORT=8080

EXPOSE 8080

COPY go.mod go.sum ./

RUN go mod download && go mod verify

COPY . .

RUN go build -o app main.go

CMD ["./app"]
