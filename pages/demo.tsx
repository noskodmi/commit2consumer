import { useEffect } from "react";
import { useRouter } from "next/router";

const LOOM_URL = "https://www.loom.com/share/d2e729d014824b50b54f02f4cc307f8f?sid=41c34bff-581c-451f-98d3-89abe4caa4f1";

export default function Demo() {
  const router = useRouter();
  useEffect(() => {
    // Prefer replace to avoid back button loop
    router.replace(LOOM_URL);
  }, [router]);
  return null;
}