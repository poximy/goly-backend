FROM golang:1.17-bullseye

WORKDIR /app

COPY . .

COPY go.mod go.sum ./

RUN go mod download && go mod verify

COPY . .

RUN go build -o server

CMD ["./server"]
