import ThemeToggler from "@/components/theme/toggler";
import { Button } from "@/components/ui/button";
import { UserProfile } from "@/components/user-profile";
import { siteConfig } from "@/config/site.config";
import { Plus, FolderOpen, BarChart2, CreditCard, Layout, Settings, Users, Search, Camera } from "lucide-react";
import Link from "next/link";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="w-full h-screen overflow-hidden flex flex-col">
      <MockNavbar />
      <div className="flex h-full">
        <MockSidebar />
        <div id="main" className="flex-1 overflow-y-auto">
          {children}
        </div>
      </div>
    </div>
  )
}

const MockNavbar = () => {
  return (
    <div id="nav" className="border-b border-dashed flex items-center justify-between">
      <div id="brand" className="h-full md:border-r border-dashed w-[200px] flex items-center justify-center">
        <Button variant="ghost" className="w-full h-full font-heading text-lg md:text-2xl font-bold" asChild>
          <Link href="/">
            <span>{siteConfig.name}</span>
          </Link>
        </Button>
      </div>
      <div className="flex-1 flex items-center justify-end h-full border-dashed divide-x">
        <Button className="h-full border-l border-dashed" size="lg" variant="ghost" asChild>
          <Link href="/projects/new" className="flex items-center gap-2">
            <Plus className="size-4" />
            <span>Add Project</span>
          </Link>
        </Button>
        <Button className="h-full border-l border-dashed" size="lg" variant="ghost" asChild>
          <Link href="/projects" className="flex items-center gap-2">
            <FolderOpen className="size-4" />
            <span>View Projects</span>
          </Link>
        </Button>
        <ThemeToggler className="h-full border-dashed size-10 md:size-14" />
        <UserProfile className="size-10 md:size-14" />
      </div>
    </div>
  )
}

const MockSidebar = () => {
  return (
    <div id="sidebar" className="w-[200px] border-r border-dashed hidden md:block">
      <div className="flex flex-col divide-y border-b border-dashed">
        <Button variant="ghost" className="border-dashed h-14 text-left justify-start pl-8" asChild>
          <Link href="/dashboard">
            <BarChart2 />
            <span>Creator Hub</span>
          </Link>
        </Button>
         <Button variant="ghost" className="border-dashed h-14 text-left justify-start pl-8" asChild>
          <Link href="/projects">
            <FolderOpen />
            <span>Projects</span>
          </Link>
        </Button>
        <Button variant="ghost" className="border-dashed h-14 text-left justify-start pl-8" asChild>
          <Link href="/find">
            <Search />
            <span>Find using text</span>
          </Link>
        </Button>
        {/* New: Find by Image */}
        <Button variant="ghost" className="border-dashed h-14 text-left justify-start pl-8" asChild>
          <Link href="/find-by-image">
            <Camera />
            <span>Find using image</span>
          </Link>
        </Button>
      </div>
    </div>
  )
}