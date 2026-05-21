# http-ranger

A lightweight API testing tool that runs in your terminal. No bloated UI, no electron apps—just fast, scriptable HTTP testing with built-in automation and performance benchmarking.

## Features

- **Terminal-native** - Works in any shell, SSH session, or CI pipeline
- **Fast startup** - No GUI to load, sub-second response times
- **Automated testing** - Write test suites in YAML or JSON
- **Performance benchmarking** - Built-in load testing with latency percentiles
- **Scriptable** - Pipe-friendly output, integrates with shell workflows
- **Multi-environment** - Switch between dev, staging, and prod configs instantly

## Installation

```bash
# macOS
brew install http-ranger

# Linux
curl -sSL https://get.httpranger.dev | sh

# Cargo (Rust)
cargo install http-ranger

# Go
 go install github.com/httpranger/cli@latest
```

## Quick Start

Send a simple GET request:

```bash
http-ranger get https://api.example.com/users
```

With headers and query params:

```bash
http-ranger get https://api.example.com/users \
  -H "Authorization: Bearer $TOKEN" \
  -q "page=1" \
  -q "limit=20"
```

POST with JSON body:

```bash
http-ranger post https://api.example.com/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "email": "alice@example.com"}'
```

## Automated Testing

Define test suites in YAML:

```yaml
# tests.yaml
base_url: https://api.example.com

headers:
  Authorization: Bearer ${API_TOKEN}
  Content-Type: application/json

tests:
  - name: "Get user list"
    method: GET
    path: /users
    expect:
      status: 200
      json_path:
        $.data: exists
        $.data[0].id: is_number

  - name: "Create user"
    method: POST
    path: /users
    body:
      name: Test User
      email: test@example.com
    expect:
      status: 201
      json_path:
        $.id: is_number
        $.name: "Test User"

  - name: "Get single user"
    method: GET
    path: /users/${created_user_id}
    expect:
      status: 200
      header:
        Content-Type: "application/json"
```

Run the suite:

```bash
http-ranger test tests.yaml
```

Output:

```
✓ Get user list (45ms)
✓ Create user (120ms)
✓ Get single user (38ms)

3 passed, 0 failed
```

## Performance Benchmarking

Run a load test:

```bash
http-ranger bench https://api.example.com/users \
  -n 10000 \
  -c 100 \
  -H "Authorization: Bearer $TOKEN"
```

Results:

```
Benchmark Results
=================
Requests:      10,000
Concurrency:   100
Duration:      2.34s

Latency:
  Min:         12ms
  Avg:         23ms
  P50:         21ms
  P90:         35ms
  P95:         42ms
  P99:         68ms
  Max:         156ms

Throughput:    4,273 req/sec

Status Codes:
  200:         9,987
  500:         13

Errors:        0
```

## Configuration

Create a `.http-ranger.yaml` in your project root:

```yaml
environments:
  dev:
    base_url: http://localhost:3000
    headers:
      X-Debug: "true"

  staging:
    base_url: https://staging-api.example.com
    headers:
      Authorization: Bearer ${STAGING_TOKEN}

  prod:
    base_url: https://api.example.com
    headers:
      Authorization: Bearer ${PROD_TOKEN}

defaults:
  timeout: 30s
  retries: 3
  follow_redirects: true
```

Switch environments:

```bash
http-ranger --env staging get /users
```

## Scripting & Piping

http-ranger outputs clean JSON for shell integration:

```bash
# Extract specific fields with jq
http-ranger get https://api.example.com/users | jq '.data[].email'

# Chain requests
USER_ID=$(http-ranger post https://api.example.com/users -d '{"name":"test"}' | jq -r '.id')
http-ranger get "https://api.example.com/users/$USER_ID"

# Use in CI
http-ranger test tests.yaml --fail-fast || exit 1
```

## Comparison

| Feature | http-ranger | Postman | cURL |
|---------|-------------|---------|------|
| Terminal-native | ✓ | ✗ | ✓ |
| Startup time | <100ms | 3-5s | <50ms |
| Test automation | ✓ | ✓ | ✗ |
| Performance testing | ✓ | Paid | ✗ |
| CI/CD integration | ✓ | Limited | ✓ |
| Collection sharing | Git | Cloud | ✗ |
| GUI | ✗ | ✓ | ✗ |

## Commands

```
http-ranger [command] [options]

Commands:
  get, post, put, patch, delete   HTTP methods
  test                            Run test suite
  bench                           Run benchmark
  env                             Manage environments
  config                          Show/edit configuration

Options:
  -H, --header       Add header
  -d, --data         Request body
  -q, --query        Query parameter
  -t, --timeout      Request timeout
  -e, --env          Environment to use
  -o, --output       Output format (json, yaml, table)
  -v, --verbose      Verbose output
  --fail-fast        Stop on first failure (test mode)
```

## Contributing

Contributions are welcome. Open an issue to discuss changes or submit a pull request.

```bash
git clone https://github.com/httpranger/http-ranger.git
cd http-ranger
cargo build --release
```

## License

MIT
