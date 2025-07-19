"use client";

import { useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Camera } from "lucide-react";

export default function FindByImagePage() {
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedImage(file);
      setPreviewUrl(URL.createObjectURL(file));
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Implement API call to find clips by image
    alert("Feature coming soon! This will find matching clips using your image.");
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-[70vh] w-full">
      <Card className="w-full max-w-lg mx-auto p-6 shadow-lg">
        <CardHeader className="flex flex-col items-center gap-2">
          <Camera className="w-10 h-10 text-primary mb-2" />
          <CardTitle className="text-2xl font-bold text-center">Find using image</CardTitle>
          <p className="text-muted-foreground text-center text-sm mt-1">
            Upload an image and let AI find matching moments in your footage.
          </p>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="flex flex-col gap-6 items-center">
            <label className="w-full flex flex-col items-center gap-2 cursor-pointer">
              <span className="text-sm font-medium">Select an image</span>
              <input
                type="file"
                accept="image/*"
                onChange={handleImageChange}
                className="hidden"
              />
              <div className="w-40 h-40 bg-muted border-2 border-dashed rounded-lg flex items-center justify-center overflow-hidden">
                {previewUrl ? (
                  <img src={previewUrl} alt="Preview" className="object-cover w-full h-full" />
                ) : (
                  <span className="text-muted-foreground text-4xl">🖼️</span>
                )}
              </div>
            </label>
            <Button type="submit" disabled={!selectedImage} className="w-full">
              Find Clips
            </Button>
          </form>
          {/* Placeholder for results */}
          <div className="mt-8 text-center text-muted-foreground text-sm">
            {/* Results will appear here */}
            <span>Results will appear here after you upload an image.</span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 