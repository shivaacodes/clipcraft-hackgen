"use client";

import Link from "next/link";
import { FolderOpen } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function OpenProjectButton() {
  return (
    <div className="flex flex-col items-center justify-center h-[80vh] text-center space-y-4">
      <h1 className="text-3xl font-bold">
        🚀 Ready to dive back into your work?
      </h1>
      <p className="text-muted-foreground text-sm max-w-md">
        Your projects are waiting, your creativity is calling ✨. Click below to jump back in and make some magic!
      </p>
      <Link href="/projects">
        <Button variant="default" className="text-base px-6 py-4">
          <FolderOpen className="w-5 h-5 mr-2" />
          Open Project
        </Button>
      </Link>
    </div>
  );
}
