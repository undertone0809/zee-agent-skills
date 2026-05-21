# nano-store

A tiny, feature-complete state management library for React. Just 1KB.

## Features

- **Atomic state** - Create simple, reactive state atoms
- **Derived state** - Compute values from other atoms with automatic updates
- **Async actions** - Handle asynchronous operations with built-in loading states
- **React integration** - Hooks for subscribing to state changes
- **TypeScript support** - Fully typed out of the box

## Installation

```bash
npm install nano-store
```

## Quick Start

```tsx
import { atom, useAtom } from 'nano-store';

// Create an atom
const count = atom(0);

function Counter() {
  const [value, setValue] = useAtom(count);

  return (
    <button onClick={() => setValue(value + 1)}>
      Count: {value}
    </button>
  );
}
```

## API

### `atom(initialValue)`

Creates a new state atom.

```ts
import { atom } from 'nano-store';

const name = atom('Alice');
const user = atom({ id: 1, name: 'Bob' });
```

### `useAtom(atom)`

React hook to subscribe to an atom's value.

```tsx
import { useAtom } from 'nano-store';

function UserProfile() {
  const [user, setUser] = useAtom(userAtom);
  return <div>{user.name}</div>;
}
```

### `derived(getter)`

Creates derived state that updates when its dependencies change.

```ts
import { atom, derived } from 'nano-store';

const firstName = atom('John');
const lastName = atom('Doe');

const fullName = derived((get) => {
  return `${get(firstName)} ${get(lastName)}`;
});
```

### `action(handler)`

Creates an async action with loading state support.

```ts
import { atom, action } from 'nano-store';

const user = atom(null);
const loading = atom(false);

const fetchUser = action(async (get, set, userId: number) => {
  set(loading, true);
  const response = await fetch(`/api/users/${userId}`);
  const data = await response.json();
  set(user, data);
  set(loading, false);
});

// In component
function UserCard({ userId }: { userId: number }) {
  const [userData] = useAtom(user);
  const [isLoading] = useAtom(loading);

  return (
    <div>
      {isLoading ? (
        <p>Loading...</p>
      ) : (
        <p>{userData?.name}</p>
      )}
      <button onClick={() => fetchUser(userId)}>Load User</button>
    </div>
  );
}
```

## Examples

### Counter with Derived State

```tsx
import { atom, derived, useAtom } from 'nano-store';

const count = atom(0);
const doubled = derived((get) => get(count) * 2);

function Counter() {
  const [value, setValue] = useAtom(count);
  const [doubleValue] = useAtom(doubled);

  return (
    <div>
      <p>Count: {value}</p>
      <p>Doubled: {doubleValue}</p>
      <button onClick={() => setValue(value + 1)}>Increment</button>
    </div>
  );
}
```

### Todo List

```tsx
import { atom, useAtom } from 'nano-store';

interface Todo {
  id: number;
  text: string;
  done: boolean;
}

const todos = atom<Todo[]>([]);

function TodoList() {
  const [items, setItems] = useAtom(todos);

  const addTodo = (text: string) => {
    setItems([...items, { id: Date.now(), text, done: false }]);
  };

  const toggleTodo = (id: number) => {
    setItems(
      items.map((todo) =>
        todo.id === id ? { ...todo, done: !todo.done } : todo
      )
    );
  };

  return (
    <div>
      {items.map((todo) => (
        <div
          key={todo.id}
          onClick={() => toggleTodo(todo.id)}
          style={{ textDecoration: todo.done ? 'line-through' : 'none' }}
        >
          {todo.text}
        </div>
      ))}
    </div>
  );
}
```

## Why nano-store?

| Library | Size | Atomic | Derived | Async |
|---------|------|--------|---------|-------|
| nano-store | 1KB | Yes | Yes | Yes |
| Redux | 5KB+ | No | No | Manual |
| Zustand | 2KB | Yes | No | Manual |
| Jotai | 3KB | Yes | Yes | Yes |

## License

MIT
