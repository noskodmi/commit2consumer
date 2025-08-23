// This page won't actually render because Next.js redirect handles it at the edge.
// It's kept here as a safeguard during local dev if redirects config is changed.
export default function DemoFallback() {
  return null;
}