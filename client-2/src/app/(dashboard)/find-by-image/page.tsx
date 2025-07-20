"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Camera, UploadCloud, Video } from "lucide-react";

// Define an interface for the clip data for better type safety
interface ClipData {
  id: number;
  start: number;
  end: number;
  duration: number;
  url: string; // The URL to the generated video clip
}

export default function FindByImagePage() {
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [previewImageUrl, setPreviewImageUrl] = useState<string | null>(null);
  const [selectedVideo, setSelectedVideo] = useState<File | null>(null);
  const [previewVideoUrl, setPreviewVideoUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [clips, setClips] = useState<ClipData[] | null>(null); // Changed from timestamps to clips

  // Updated API endpoint to match the new router prefix and endpoint
  const API_ENDPOINT = "http://localhost:8000/api/v1/find/by-image"; // Updated URL

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedImage(file);
      setPreviewImageUrl(URL.createObjectURL(file));
      setError(null); // Clear any previous errors
      setClips(null); // Clear previous results
    }
  };

  const handleVideoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedVideo(file);
      setPreviewVideoUrl(URL.createObjectURL(file));
      setError(null); // Clear any previous errors
      setClips(null); // Clear previous results
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null); // Clear previous errors
    setClips(null); // Clear previous results

    if (!selectedImage || !selectedVideo) {
      setError("Please select both an image and a video to find clips.");
      return;
    }

    setLoading(true);

    const formData = new FormData();
    formData.append("video_file", selectedVideo);
    formData.append("image_file", selectedImage);

    try {
      const response = await fetch(API_ENDPOINT, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Something went wrong with the API call.");
      }

      const data = await response.json();
      console.log("API Response:", data);
      setClips(data.clips); // Set the 'clips' state

    } catch (err: any) {
      console.error("Error finding clips:", err);
      setError(err.message || "Failed to find clips. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center w-full p-6 py-12 mt-12 min-h-screen pb-20">
      <Camera className="w-12 h-12 text-primary mb-4" />
      <h1 className="text-4xl font-extrabold text-center mb-3 leading-tight">
        Picture This! 📸 Find Your Perfect Clip
      </h1>
      <p className="text-muted-foreground text-center text-lg mb-8">
        Upload your raw video footage and an image. Our AI, powered by OpenCV, intelligently analyzes your content to automatically pinpoint and extract relevant clips that match your image.
      </p>
      <form onSubmit={handleSubmit} className="flex flex-col gap-8 items-center w-full">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 w-full">
          {/* Video Upload Option */}
          <label className="flex flex-col items-center gap-4 cursor-pointer p-8 border-2 border-dashed border-primary/50 hover:border-primary transition-all duration-300 bg-gradient-to-br from-background/50 to-background/80 shadow-inner w-full min-w-[320px]">
            <span className="text-xl font-semibold text-primary">Upload your video footage! 🎥</span>
            <input
              type="file"
              accept="video/*"
              onChange={handleVideoChange}
              className="hidden"
            />
            <div className="w-full h-72 bg-muted border-4 border-primary/30 flex items-center justify-center overflow-hidden shadow-lg">
              {previewVideoUrl ? (
                <video src={previewVideoUrl} controls className="object-cover w-full h-full" />
              ) : (
                <div className="flex flex-col items-center text-muted-foreground">
                  <Video className="w-16 h-16 mb-2" />
                  <span className="text-lg font-medium">Upload Video</span>
                </div>
              )}
            </div>
            {selectedVideo && (
              <p className="text-sm text-muted-foreground mt-2">Selected: {selectedVideo.name} 🎉</p>
            )}
          </label>

          {/* Image Upload Option */}
          <label className="flex flex-col items-center gap-4 cursor-pointer p-8 border-2 border-dashed border-primary/50 hover:border-primary transition-all duration-300 bg-gradient-to-br from-background/50 to-background/80 shadow-inner w-full min-w-[320px]">
            <span className="text-xl font-semibold text-primary">Upload your reference image! 🖼️</span>
            <input
              type="file"
              accept="image/*"
              onChange={handleImageChange}
              className="hidden"
            />
            <div className="w-full h-72 bg-muted border-4 border-primary/30 flex items-center justify-center overflow-hidden shadow-lg">
              {previewImageUrl ? (
                <img src={previewImageUrl} alt="Preview" className="object-cover w-full h-full" />
              ) : (
                <div className="flex flex-col items-center text-muted-foreground">
                  <UploadCloud className="w-16 h-16 mb-2" />
                  <span className="text-lg font-medium">Upload Image</span>
                </div>
              )}
            </div>
            {selectedImage && (
              <p className="text-sm text-muted-foreground mt-2">Selected: {selectedImage.name} 🎉</p>
            )}
          </label>
        </div>

        {error && (
          <p className="text-red-500 text-center font-semibold">{error}</p>
        )}

        <Button
          type="submit"
          disabled={!selectedImage || !selectedVideo || loading}
          className="w-full text-lg py-3 font-bold shadow-lg hover:shadow-xl transition-all duration-300 mb-12"
        >
          {loading ? "Finding Clips..." : "Find My Clips! 🎉"}
        </Button>
      </form>

      {/* Display Results */}
      {clips && clips.length > 0 && (
        <div className="mt-12 w-full">
          <h2 className="text-3xl font-bold text-center mb-8 text-primary">Potential Matches Found! ✨</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {clips.map((clip) => ( // Iterate over 'clips'
              <div key={clip.id} className="flex flex-col items-center gap-4 p-6 bg-card border border-muted-foreground/10 shadow-lg rounded-lg">
                <div className="w-full h-40 bg-muted flex items-center justify-center overflow-hidden rounded-md">
                  {/* Use the actual clip URL here */}
                  <video
                    src={"http://localhost:8000"+clip.url}
                    controls
                    className="object-cover w-full h-full"
                    preload="metadata" // Load only metadata initially for faster rendering
                  />
                </div>
                <h3 className="text-xl font-semibold text-center">Clip {clip.id}</h3>
                <p className="text-sm text-muted-foreground text-center">
                  Start: {clip.start.toFixed(2)}s, End: {clip.end.toFixed(2)}s, Duration: {clip.duration.toFixed(2)}s
                </p>
                {/* Removed "View Clip" button as the video is embedded directly */}
              </div>
            ))}
          </div>
        </div>
      )}

      {clips && clips.length === 0 && !loading && !error && (
        <div className="mt-12 w-full text-center text-lg text-muted-foreground">
          <p>No character presence periods were detected in the video with the provided image.</p>
          <p>Try a different image or video, or adjust detection parameters (on the backend).</p>
        </div>
      )}
    </div>
  );
}