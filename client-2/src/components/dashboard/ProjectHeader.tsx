import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft } from "lucide-react";
import React from "react";

interface ProjectHeaderProps {
  project: {
    name: string;
    description?: string;
    type?: string;
    language?: string;
    genre?: string;
  };
  onBack: () => void;
}

export default function ProjectHeader({ project, onBack }: ProjectHeaderProps) {
  return (
    <div className="flex items-center gap-4 mb-6">
      <Button variant="ghost" size="sm" onClick={onBack}>
        <ArrowLeft className="w-4 h-4 mr-2" />
        Back to Projects
      </Button>
      <div>
        <h1 className="text-2xl font-bold">{project.name}</h1>
        <p className="text-sm text-muted-foreground">{project.description}</p>
        <div className="flex gap-2 mt-1">
          {project.type && <Badge variant="secondary">{project.type}</Badge>}
          {project.language && <Badge variant="outline">{project.language}</Badge>}
          {project.genre && <Badge variant="outline">{project.genre}</Badge>}
        </div>
      </div>
    </div>
  );
} 