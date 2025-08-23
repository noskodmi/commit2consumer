import { useEffect } from "react";
import { useRouter } from "next/router";

export default function Home() {
  const router = useRouter();
  useEffect(() => {
    router.replace("https://narrow-stamp-35953767.figma.site/");
  }, [router]);

  return null;
}