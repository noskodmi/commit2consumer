import Link from "next/link";

export default function Home() {
  return (
    <main
      style={{
        fontFamily: "system-ui, sans-serif",
        padding: "2rem",
        lineHeight: 1.5
      }}
    >
      <h1>Vercel Redirect Demo</h1>
      <p>
        Visit <Link href="/demo">/demo</Link> to be redirected to the Loom
        video.
      </p>
    </main>
  );
}