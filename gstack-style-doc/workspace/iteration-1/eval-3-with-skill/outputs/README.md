# nano-store

> "State management doesn't need to be a framework. It needs to disappear."

Last year, our bundle analyzer showed Redux + Toolkit + Thunk was 18KB gzipped. For a form with three fields. We spent more time wiring actions than building features.

I wanted something that just worked. No boilerplate. No context providers. No re-renders when I didn't need them.

So I built nano-store. **1KB.** Atomic state. Derived state. Async actions. Everything you actually use, nothing you don't.

## 30-Second Start

```bash
npm install nano-store
```

```tsx
import { atom, useAtom } from 'nano-store'

// Atomic state
const count = atom(0)

// Derived state
const doubled = atom((get) => get(count) * 2)

function Counter() {
  const [value, setValue] = useAtom(count)
  const [double] = useAtom(doubled)

  return (
    <button onClick={() => setValue(v => v + 1)}>
      {value} × 2 = {double}
    </button>
  )
}
```

## Core Workflow: Write State, Not Wiring

You said: "I need global state for my cart."

nano-store said: "Write one line. Use it anywhere."

```ts
// store/cart.ts
export const cartItems = atom<Item[]>([])
export const cartTotal = atom((get) =>
  get(cartItems).reduce((sum, item) => sum + item.price, 0)
)
```

```tsx
// components/CartBadge.tsx
import { useAtom } from 'nano-store'
import { cartItems } from '../store/cart'

export function CartBadge() {
  const [items] = useAtom(cartItems)
  // Only re-renders when cartItems changes
  return <span>{items.length}</span>
}
```

```tsx
// components/AddToCart.tsx
import { useSetAtom } from 'nano-store'
import { cartItems } from '../store/cart'

export function AddToCart({ item }) {
  const setItems = useSetAtom(cartItems)
  // This component never re-renders on cart changes
  return <button onClick={() => setItems(prev => [...prev, item])}>Add</button>
}
```

You said: "But I need async actions."

nano-store said: "Atoms can be async. Components just subscribe."

```ts
// store/user.ts
export const userId = atom<string | null>(null)

export const userProfile = atom(async (get) => {
  const id = get(userId)
  if (!id) return null
  const res = await fetch(`/api/users/${id}`)
  return res.json()
})
```

```tsx
function UserCard() {
  const [profile] = useAtom(userProfile)
  // Suspense-ready: handles loading states automatically
  return profile ? <h1>{profile.name}</h1> : <Spinner />
}
```

Three patterns, zero boilerplate. This isn't a state library. It's a state removal tool.

## Your State Toolkit

| Pattern | Your Use Case | What You Get |
|---------|---------------|--------------|
| `atom(value)` | Simple state | Reactive primitive, any scope |
| `atom(deriveFn)` | Computed values | Auto-updates when deps change |
| `atom(asyncFn)` | Data fetching | Suspense integration, caching |
| `useAtom(atom)` | Read + write | Subscribe to updates |
| `useSetAtom(atom)` | Write only | Zero re-renders on updates |
| `useAtomValue(atom)` | Read only | Optimized for derived data |

## Why This Approach

**Not Redux:** No actions, reducers, or store configuration. You write state, not wiring.

**Not Context:** No provider trees, no performance footguns. Components subscribe to exactly what they need.

**Not Signals:** No framework lock-in. Works with React today, Vue/Svelte tomorrow.

**The trade-off:** We don't have time-travel debugging or middleware. If you need those, Redux Toolkit is excellent. For the other 90% of state, nano-store is enough.

## Bundle Size Comparison

| Library | Size (gzipped) |
|---------|----------------|
| Redux + Toolkit + Thunk | ~18KB |
| Zustand | ~3KB |
| Jotai | ~4KB |
| **nano-store** | **~1KB** |

Measured on bundlephobia, React bindings included.

## Deeper Reading

- [API Reference](./docs/api.md) — All exports, all options
- [Recipes](./docs/recipes.md) — Patterns for common use cases
- [How It Works](./docs/internals.md) — The 200-line implementation

Fork it. Improve it. Make it yours.
