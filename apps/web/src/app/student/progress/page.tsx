"use client";

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function ProgressRedirect() {
  const router = useRouter();
  useEffect(() => {
    router.replace('/student/batch');
  }, [router]);
  return null;
}
