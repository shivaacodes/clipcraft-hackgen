"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { 
  Video, 
  Image, 
  Music, 
  FileText, 
  Presentation, 
  Code, 
  Palette,
  ArrowLeft,
  Plus 
} from "lucide-react";
import { useRouter } from "next/navigation";

const projectTypes = [
  { id: "video", label: "Video Project", icon: Video, description: "Create and edit video content", color: "bg-blue-500", lightColor: "bg-blue-100", darkColor: "bg-blue-900" },
  { id: "image", label: "Image Gallery", icon: Image, description: "Photo slideshow and gallery", color: "bg-green-500", lightColor: "bg-green-100", darkColor: "bg-green-900" },
  { id: "music", label: "Music Video", icon: Music, description: "Audio-visual music content", color: "bg-purple-500", lightColor: "bg-purple-100", darkColor: "bg-purple-900" },
  { id: "documentary", label: "Documentary", icon: FileText, description: "Documentary style content", color: "bg-orange-500", lightColor: "bg-orange-100", darkColor: "bg-orange-900" },
  { id: "presentation", label: "Presentation", icon: Presentation, description: "Business presentations", color: "bg-red-500", lightColor: "bg-red-100", darkColor: "bg-red-900" },
  { id: "tutorial", label: "Tutorial", icon: Code, description: "Educational content", color: "bg-indigo-500", lightColor: "bg-indigo-100", darkColor: "bg-indigo-900" },
  { id: "creative", label: "Creative", icon: Palette, description: "Artistic and creative projects", color: "bg-pink-500", lightColor: "bg-pink-100", darkColor: "bg-pink-900" },
];

const languages = [
  { label: "English", value: "en" },
  { label: "Hindi", value: "hi" },
  { label: "Malayalam", value: "ml" },
];

const genres = [
  "Action",
  "Romance",
  "Thriller",
  "Comedy",
  "Drama",
  "Documentary",
  "Fantasy/Sci-Fi"
];

export default function NewProjectPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    name: "",
    type: "",
    language: "en", // Default to English
    genre: "",
  });
  const [showTypeDialog, setShowTypeDialog] = useState(false);

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleCreateProject = async () => {
    try {
      const response = await fetch("/api/projects", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: formData.name,
          type: formData.type,
          language: formData.language, // Store language code in DB
          genre: formData.genre,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to create project");
      }

      const data = await response.json();
      
      // Redirect to the new project's individual page
      router.push(`/projects/${data.project.id}`);
    } catch (error) {
      console.error("Error creating project:", error);
      // You might want to show an error message to the user here
    }
  };

  const handleTypeSelect = (type: string) => {
    handleInputChange("type", type);
    setShowTypeDialog(false);
  };

  const selectedType = projectTypes.find(type => type.id === formData.type);

  return (
    <div className="p-6 pb-12 max-w-4xl mx-auto">
      <div className="flex items-center gap-4 mb-6">
        <Button variant="ghost" size="sm" onClick={() => router.back()}>
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </Button>
        <div>
          <h1 className="text-2xl font-bold">Create New Project</h1>
          <p className="text-muted-foreground">
            Set up your new video project with custom settings
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Project Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">Project Name</Label>
              <Input
                id="name"
                placeholder="Enter project name"
                value={formData.name}
                onChange={(e) => handleInputChange("name", e.target.value)}
              />
            </div>


            <div className="space-y-2">
              <Label>Project Type</Label>
              <Dialog open={showTypeDialog} onOpenChange={setShowTypeDialog}>
                <DialogTrigger asChild>
                  <Button variant="outline" className="w-full justify-start">
                    {selectedType ? (
                      <div className="flex items-center gap-2">
                        <selectedType.icon className="w-4 h-4" />
                        {selectedType.label}
                      </div>
                    ) : (
                      <div className="flex items-center gap-2">
                        <Plus className="w-4 h-4" />
                        Select project type
                      </div>
                    )}
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-2xl">
                  <DialogHeader>
                    <DialogTitle>Choose Project Type</DialogTitle>
                  </DialogHeader>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {projectTypes.map((type) => (
                      <Card 
                        key={type.id} 
                        className="cursor-pointer hover:shadow-md transition-all duration-200 hover:scale-105 border-0 overflow-hidden"
                        onClick={() => handleTypeSelect(type.id)}
                      >
                        <CardContent className="p-0">
                          <div className={`h-2 ${type.color}`}></div>
                          <div className="p-4">
                            <div className="flex items-center gap-3 mb-2">
                              <div className={`p-2 rounded-full ${type.lightColor} dark:${type.darkColor}`}>
                                <type.icon className={`w-5 h-5 ${type.color.replace('bg-', 'text-')}`} />
                              </div>
                              <h3 className="font-semibold">{type.label}</h3>
                            </div>
                            <p className="text-sm text-muted-foreground">
                              {type.description}
                            </p>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </DialogContent>
              </Dialog>
            </div>

            <div className="space-y-2">
              <Label>Language</Label>
              <Select value={formData.language} onValueChange={(value) => handleInputChange("language", value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select language" />
                </SelectTrigger>
                <SelectContent>
                  {languages.map((lang) => (
                    <SelectItem key={lang.value} value={lang.value}>
                      {lang.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Project Settings</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Genre</Label>
              <Select onValueChange={(value) => handleInputChange("genre", value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select genre" />
                </SelectTrigger>
                <SelectContent>
                  {genres.map((genre) => (
                    <SelectItem key={genre} value={genre.toLowerCase()}>
                      {genre}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>


            <div className="pt-4 border-t">
              <h4 className="font-semibold mb-2">Project Summary</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Name:</span>
                  <span>{formData.name || "—"}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Type:</span>
                  <span>{selectedType?.label || "—"}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Language:</span>
                  <span>{formData.language || "—"}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Genre:</span>
                  <span>{formData.genre || "—"}</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="flex items-center justify-end gap-4 mt-6">
        <Button variant="outline" onClick={() => router.back()}>
          Cancel
        </Button>
        <Button 
          onClick={handleCreateProject}
          disabled={!formData.name || !formData.type}
        >
          Create Project
        </Button>
      </div>
    </div>
  );
}