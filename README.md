# Goly Backend

Goly is inspired by [`bit.ly`](https://bitly.com/)

Web app is live at [goly.poximy.com](https://goly.poximy.com)

Built with `.go` and [`chi`](https://github.com/go-chi/chi)

## API

### Redirects to original url

[ID] is a randomly generated

`/[ID] GET 301`

### Creates a shortened url

`/ POST 201`

request:

```json
{
  "url": "https://goly.vercel.app"
}
```

response:

```json
{
  "id": "123456",
  "url": "https://goly.vercel.app",
  "clicks": 0
}
```
