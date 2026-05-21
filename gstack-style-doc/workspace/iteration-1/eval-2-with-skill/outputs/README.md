# http-ranger

> "Postman is a cockpit. Sometimes you just need a compass and a good pair of boots."

Last quarter, our team spent more time waiting for Postman to load than actually testing APIs. 12 seconds to launch. 47 clicks to run a saved collection. 3 different auth flows to reconfigure every time the token expired.

We were doing simple health checks. Simple GET requests. Simple validation that an endpoint still responded.

http-ranger doesn't replace your API platform. It replaces the 80% of API testing that should be instant, scriptable, and invisible.

## 30-Second Start

```bash
# Installation
cargo install http-ranger

# First request
hr get https://api.github.com/user

# Run a test suite
hr run tests/auth.yml
```

## Core Workflow: The 3-Second API Check

You: `hr get https://api.example.com/health`

http-ranger:
- Status: 200 OK (23ms)
- Response: `{"status":"healthy","version":"2.4.1"}`
- [PASS] JSON schema matches expected structure

You: `hr run tests/ --parallel=10`

http-ranger:
- 47 tests completed in 1.2s
- 46 passed, 1 failed (timeout on `/slow-endpoint`)
- [BENCHMARK] p50: 45ms, p99: 890ms, throughput: 391 req/s

This isn't a GUI wrapper around curl. It's a testing runtime that happens to fit in your terminal.

## Your API Testing Team

| Command | Your Specialist | What They Do |
|---------|-----------------|--------------|
| `get/post/put/delete` | API Explorer | One-off requests with instant feedback |
| `run` | Test Engineer | Execute test suites with assertions |
| `bench` | Performance Analyst | Load testing with latency distributions |
| `watch` | SRE Monitor | Continuous polling with alert thresholds |
| `env` | DevOps Coordinator | Manage environments, secrets, and contexts |
| `export` | CI/CD Integrator | Convert to curl, HAR, or CI pipeline configs |

## Why Terminal-First

You said: "I need a lighter Postman."

http-ranger said: "You're not looking for lighter software. You're looking for faster decisions."

**The trade-off:** No GUI means no clicking through collections. But it also means:
- Tests live in git, reviewed in PRs
- CI pipelines run the exact same tests you run locally
- 47ms startup time vs 12 seconds
- Your hands never leave the keyboard

**When to use Postman:** API documentation, team collaboration, complex OAuth flows
**When to use http-ranger:** Daily development, regression testing, performance baselines, incident response

## Test Definition (YAML)

```yaml
# tests/users.yml
name: User API Suite
base_url: ${{ env.API_URL }}

tests:
  - name: Get current user
    method: GET
    path: /me
    headers:
      Authorization: Bearer ${{ secrets.TOKEN }}
    expect:
      status: 200
      json:
        id: ${{ type.number }}
        email: ${{ match.email }}

  - name: Create user validation
    method: POST
    path: /users
    body:
      email: invalid-email
    expect:
      status: 400
      json:
        error: "Invalid email format"
```

## Benchmark Mode

```bash
$ hr bench https://api.example.com/search --duration=30s --concurrency=50

Running 50 concurrent connections for 30s...

Latency Distribution:
  50%:    23ms
  75%:    45ms
  90%:   120ms
  99%:   890ms

Throughput: 391 req/s
Errors: 0.02% (3 timeout, 1 connection reset)

Baseline saved to .hr/baselines/search-2024-01-15.json
[ALERT] p99 increased 23% since last run
```

## Deeper Reading

- [Test Syntax Reference](./docs/test-syntax.md)
- [CI/CD Integration](./docs/ci-integration.md)
- [Performance Benchmarking Guide](./docs/benchmarking.md)
- [Why We Chose Rust](./docs/philosophy.md)
