"use client";

import { useState, useRef, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  UploadCloud,
  Scissors,
  Upload,
  Music,
  Wand2,
  Plus,
  Play,
  Pause,
  Volume2,
  Trash2,
  Download,
  Move,
  ArrowLeft,
  Settings,
  Share2,
  Save,
  X,
  Clock,
  Check,
  Users,
  ChevronDown,
  AlertTriangle,
} from "lucide-react";
import { FaWhatsapp, FaInstagram, FaYoutube } from "react-icons/fa";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import BgmDialog from "./BgmDialog";
import SoundEffectsDialog from "./SoundEffectsDialog";
import AudioTrack, { AudioItem } from "./AudioTrack";
import ProjectHeader from "@/components/dashboard/ProjectHeader";
import VibeAgeBadges from "@/components/dashboard/VibeAgeBadges";
import TopActionRow from "@/components/dashboard/TopActionRow";
import VideoContentCard from "@/components/dashboard/VideoContentCard";
import GeneratedClipsCard from "@/components/dashboard/GeneratedClipsCard";
import TimelineEditorCard from "@/components/dashboard/TimelineEditorCard";
import ClipPlayerDialog from "@/components/dashboard/ClipPlayerDialog";
import RenderedVideoPreview from "@/components/dashboard/RenderedVideoPreview";

const vibes = [
  { label: "😄", value: "Happy" },
  { label: "🎭", value: "Dramatic" },
  { label: "🔥", value: "intense" },
  { label: "🎉", value: "Fun" },
  { label: "💡", value: "Inspiring" },
  { label: "🕵️", value: "Mysterious" },
  { label: "😭", value: "Emotional" },
  { label: "😎", value: "cool" },
  { label: "🎶", value: "musical" },
];

const ageGroups = [
  { label: "Kids (6-12)", value: "kids" },
  { label: "Teens (13-19)", value: "teens" },
  { label: "Young Adults (20-35)", value: "young-adults" },
  { label: "Adults (36-55)", value: "adults" },
  { label: "Seniors (55+)", value: "seniors" },
  { label: "General Audience", value: "general" },
];

export const exportPlatforms = [
  {
    id: "whatsapp",
    name: "WhatsApp Status",
    icon: FaWhatsapp,
    iconColor: "#25D366",
    dimensions: "720x1280",
    format: "MP4",
    aspectRatio: "9:16",
    duration: "30s",
    description: "Export for WhatsApp Status (max 30 seconds, vertical)"
  },
  {
    id: "instagram", 
    name: "Instagram Reel",
    icon: FaInstagram,
    iconColor: "#E4405F",
    dimensions: "1080x1920",
    format: "MP4",
    aspectRatio: "9:16",
    duration: "90s",
    description: "Export for Instagram Reels (max 90 seconds, vertical)"
  },
  {
    id: "youtube",
    name: "YouTube Shorts",
    icon: FaYoutube,
    iconColor: "#FF0000",
    dimensions: "1080x1920",
    format: "MP4",
    aspectRatio: "9:16",
    duration: "60s",
    description: "Export for YouTube Shorts (max 60 seconds, vertical)"
  }
];

interface Project {
  id: string;
  name: string;
  description?: string;
  type?: string;
  language?: string;
  genre?: string;
  durationSeconds?: number;
  thumbnailUrl?: string;
  videoUrl?: string | null; // allow null
  createdAt: string;
  updatedAt: string;
}

// Color mappings for vibes and age groups
const vibeColors: Record<string, { bg: string; text: string; border: string }> = {
  Happy: { bg: "bg-yellow-100", text: "text-yellow-700", border: "border-yellow-300" },
  Dramatic: { bg: "bg-purple-100", text: "text-purple-700", border: "border-purple-300" },
  intense: { bg: "bg-red-100", text: "text-red-700", border: "border-red-300" },
  Fun: { bg: "bg-pink-100", text: "text-pink-700", border: "border-pink-300" },
  Inspiring: { bg: "bg-blue-100", text: "text-blue-700", border: "border-blue-300" },
  Mysterious: { bg: "bg-indigo-100", text: "text-indigo-700", border: "border-indigo-300" },
  Emotional: { bg: "bg-rose-100", text: "text-rose-700", border: "border-rose-300" },
  cool: { bg: "bg-teal-100", text: "text-teal-700", border: "border-teal-300" },
  musical: { bg: "bg-emerald-100", text: "text-emerald-700", border: "border-emerald-300" },
};

const ageGroupColors: Record<string, { bg: string; text: string; border: string }> = {
  kids: { bg: "bg-lime-100", text: "text-lime-700", border: "border-lime-300" },
  teens: { bg: "bg-fuchsia-100", text: "text-fuchsia-700", border: "border-fuchsia-300" },
  "young-adults": { bg: "bg-sky-100", text: "text-sky-700", border: "border-sky-300" },
  adults: { bg: "bg-orange-100", text: "text-orange-700", border: "border-orange-300" },
  seniors: { bg: "bg-gray-100", text: "text-gray-700", border: "border-gray-300" },
  general: { bg: "bg-neutral-100", text: "text-neutral-700", border: "border-neutral-300" },
};

// Loader component (Uiverse.io by david-mohseni)
function UiverseLoader() {
  return (
    <div className="loader mx-auto my-8">
      <div className="bar1"></div>
      <div className="bar2"></div>
      <div className="bar3"></div>
      <div className="bar4"></div>
      <div className="bar5"></div>
      <div className="bar6"></div>
      <div className="bar7"></div>
      <div className="bar8"></div>
      <div className="bar9"></div>
      <div className="bar10"></div>
      <div className="bar11"></div>
      <div className="bar12"></div>
    </div>
  );
}

// Helper to compute bgm_regions for image/text segments
function computeBgmRegions(timelineItems: any[]): { start: number; duration: number }[] {
  let regions: { start: number; duration: number }[] = [];
  let currentTime = 0;
  for (const item of timelineItems) {
    const duration = parseFloat(item.duration || '3');
    if (item.type === 'image' || item.type === 'text') {
      regions.push({ start: currentTime, duration });
    }
    currentTime += duration;
  }
  return regions;
}

export default function ProjectPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [selectedVibe, setSelectedVibe] = useState<string>("");
  const [open, setOpen] = useState(false);
  const [selectedAgeGroup, setSelectedAgeGroup] = useState<string>("general");
  const [selectedVideo, setSelectedVideo] = useState<File | null>(null);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [selectedBGM, setSelectedBGM] = useState<File | null>(null);
  const [bgmUrl, setBgmUrl] = useState<string | null>(null);
  const [generatedClips, setGeneratedClips] = useState<any[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [draggedClip, setDraggedClip] = useState<any>(null);
  // Replace separate timeline states with unified timelineItems
  const [timelineItems, setTimelineItems] = useState<any[]>([]);
  const imageInputRef = useRef<HTMLInputElement>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [showExportDialog, setShowExportDialog] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [statusState, setStatusState] = useState<'queued' | 'transcribing' | 'analyzing' | 'finalizing'>('queued');
  const [showStatusIndicator, setShowStatusIndicator] = useState(false);
  const [showClipPlayer, setShowClipPlayer] = useState(false);
  const [selectedClip, setSelectedClip] = useState<any>(null);
  const [isRendering, setIsRendering] = useState(false);
  const [renderJobId, setRenderJobId] = useState<string | null>(null);
  const [fastMode, setFastMode] = useState(true);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const bgmInputRef = useRef<HTMLInputElement>(null);
  const [renderedVideoUrl, setRenderedVideoUrl] = useState<string | null>(null);
  // Add state for subtitle toggle
  const [addSubtitles, setAddSubtitles] = useState(false);
  // Add state for image and text timeline items
  const [timelineImages, setTimelineImages] = useState<any[]>([]);
  const [showBgmDialog, setShowBgmDialog] = useState(false);
  const [showSoundEffectsDialog, setShowSoundEffectsDialog] = useState(false);
  const [audioItems, setAudioItems] = useState<AudioItem[]>([]);
  const [isImporting, setIsImporting] = useState(false);
  const [uploadedBgmFilename, setUploadedBgmFilename] = useState<string | null>(null);

  // Fetch project data
  useEffect(() => {
    const fetchProject = async () => {
      try {
        setLoading(true);
        const response = await fetch(`/api/projects/${projectId}`);
        if (!response.ok) {
          throw new Error("Failed to fetch project");
        }
        const data = await response.json();
        setProject(data.project);
        
        // Load video URL if it exists
        if (data.project.videoUrl) {
          setVideoUrl(data.project.videoUrl);
          // Create a mock file for the selected video state
          const mockFile = new File([""], "uploaded-video", { type: "video/mp4" });
          setSelectedVideo(mockFile);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "An error occurred");
      } finally {
        setLoading(false);
      }
    };

    if (projectId) {
      fetchProject();
    }
  }, [projectId]);

  // If project doesn't exist after loading, redirect to projects page
  useEffect(() => {
    if (!loading && !project && !error) {
      router.push('/projects');
    }
  }, [project, loading, error, router]);

  // Status state rotation effect - only when showStatusIndicator is true
  useEffect(() => {
    if (!showStatusIndicator) return;
    
    const interval = setInterval(() => {
      setStatusState(prev => {
        switch (prev) {
          case 'queued':
            return 'transcribing';
          case 'transcribing':
            return 'analyzing';
          case 'analyzing':
            return 'finalizing';
          case 'finalizing':
            return 'queued';
          default:
            return 'queued';
        }
      });
    }, 2000);

    return () => clearInterval(interval);
  }, [showStatusIndicator]);

  // Replace project loading UI
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <UiverseLoader />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4">
        <div className="text-center py-12">
          <div className="text-red-500 text-xl mb-4">Error: {error}</div>
          <Button onClick={() => router.push('/projects')}>
            Back to Projects
          </Button>
        </div>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="p-4">
        <div className="text-center py-12">
          <div className="text-xl mb-4">Project not found</div>
          <Button onClick={() => router.push('/projects')}>
            Back to Projects
          </Button>
        </div>
      </div>
    );
  }

  const handleVideoSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const validTypes = ['video/mp4', 'video/mov', 'video/avi', 'video/mkv', 'video/webm'];
      if (!validTypes.includes(file.type)) {
        alert('Please select a valid video file (MP4, MOV, AVI, MKV, or WebM)');
        return;
      }
      if (file.size > 100 * 1024 * 1024) {
        alert('Video file size must be less than 100MB');
        return;
      }
      setIsImporting(true); // <-- show loader
      
      // Upload the video and get thumbnail
      const formData = new FormData();
      formData.append('video', file);
      
      try {
        const uploadResponse = await fetch('/api/upload', {
          method: 'POST',
          body: formData,
        });
        
        if (!uploadResponse.ok) {
          throw new Error('Upload failed');
        }
        
        const uploadData = await uploadResponse.json();
        
        // Update project with video and thumbnail data
        if (project) {
          const updatePayload: any = {};
          
          if (uploadData.thumbnailUrl) {
            updatePayload.thumbnailUrl = uploadData.thumbnailUrl;
          }
          
          if (uploadData.videoUrl) {
            updatePayload.videoUrl = uploadData.videoUrl;
          }
          
          // Add Cloudinary IDs if available
          if (uploadData.cloudinary?.thumbnailPublicId) {
            updatePayload.thumbnailCloudinaryId = uploadData.cloudinary.thumbnailPublicId;
          }
          
          if (uploadData.cloudinary?.videoPublicId) {
            updatePayload.videoCloudinaryId = uploadData.cloudinary.videoPublicId;
          }
          
          if (uploadData.cloudinary?.duration) {
            updatePayload.durationSeconds = Math.round(uploadData.cloudinary.duration);
          }
          
          await fetch(`/api/projects/${project.id}`, {
            method: 'PATCH',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(updatePayload),
          });
          
          // Update local project state
          setProject(prev => prev ? { 
            ...prev, 
            thumbnailUrl: uploadData.thumbnailUrl,
            videoUrl: uploadData.videoUrl,
            durationSeconds: uploadData.cloudinary?.duration ? Math.round(uploadData.cloudinary.duration) : prev.durationSeconds
          } : null);
        }
        
        setSelectedVideo(file);
        // Use Cloudinary URL instead of local blob URL
        setVideoUrl(uploadData.videoUrl);
        setOpen(false);
        setIsImporting(false); // <-- hide loader
      } catch (error) {
        console.error('Error uploading video:', error);
        alert('Failed to upload video. Please try again.');
        setIsImporting(false); // <-- hide loader on error
      }
    }
  };

  const handleImportClick = () => {
    fileInputRef.current?.click();
  };

  const handleRemoveVideo = async () => {
    setSelectedVideo(null);
    
    // Only revoke object URL if it's a blob URL (starts with blob:)
    if (videoUrl && videoUrl.startsWith('blob:')) {
      URL.revokeObjectURL(videoUrl);
    }
    
    setVideoUrl(null);
    
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    
    // Remove video URL from database
    if (project) {
      try {
        await fetch(`/api/projects/${project.id}`, {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            videoUrl: null,
            videoCloudinaryId: null,
          }),
        });
        
        // Update local project state
        setProject(prev => prev ? { 
          ...prev, 
          videoUrl: null
        } : null);
      } catch (error) {
        console.error('Error removing video from project:', error);
      }
    }
  };

  const handleBGMSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const validTypes = ['audio/mp3', 'audio/wav', 'audio/m4a', 'audio/ogg'];
      if (!validTypes.includes(file.type)) {
        alert('Please select a valid audio file (MP3, WAV, M4A, or OGG)');
        return;
      }
      setSelectedBGM(file);
      const url = URL.createObjectURL(file);
      setBgmUrl(url);
      // Upload BGM to backend
      const formData = new FormData();
      formData.append('file', file);
      try {
        const res = await fetch('http://localhost:8000/api/upload-bgm', {
          method: 'POST',
          body: formData,
        });
        if (!res.ok) throw new Error('BGM upload failed');
        const data = await res.json();
        setUploadedBgmFilename(data.filename); // Use backend filename
      } catch (err) {
        alert('BGM upload failed. Please try again.');
        setUploadedBgmFilename(null);
      }
    }
  };

  const handleBGMClick = () => {
    bgmInputRef.current?.click();
  };

  const handleGenerateClips = async () => {
    if (!selectedVideo || !project || !project.videoUrl) return;
    
    // Check if vibe and age group are selected
    if (!selectedVibe || !selectedAgeGroup) {
      alert('Please select a vibe and age group before generating clips.');
      return;
    }
    
    setIsGenerating(true);
    setShowStatusIndicator(true);
    setStatusState('queued');
    
    try {
      // Call backend to process video with selected vibe and age group
      const response = await fetch('http://localhost:8000/api/v1/process/process-cloudinary-video', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          video_url: project.videoUrl,
          chunk_strategy: 'adaptive',
          include_vibe_analysis: true,
          fast_mode: fastMode, // Add fast mode setting
          project_context: {
            name: project.name,
            type: project.type,
            genre: project.genre,
            language: project.language,
            selected_vibe: selectedVibe,
            selected_age_group: selectedAgeGroup
          }
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to start processing');
      }
      
      const result = await response.json();
      const jobId = result.job_id;
      
      // Poll for results
      const pollForResults = async () => {
        try {
          const statusResponse = await fetch(`http://localhost:8000/api/v1/process/status/${jobId}`);
          const statusData = await statusResponse.json();
          
          // Update status indicator based on current step
          if (statusData.current_step && statusData.current_step.includes('transcribing')) {
            setStatusState('transcribing');
          } else if (statusData.current_step && statusData.current_step.includes('analyzing_vibe')) {
            setStatusState('analyzing');
          } else if (statusData.current_step && statusData.current_step.includes('generating_clips')) {
            setStatusState('finalizing');
          }
          
          if (statusData.status === 'completed') {
            const resultResponse = await fetch(`http://localhost:8000/api/v1/process/result/${jobId}`);
            const resultData = await resultResponse.json();
            
            // Log performance data if available
            if (resultData.performance) {
              console.log('📊 Performance Analysis:', resultData.performance);
              
              const totalTime = resultData.performance.total_time;
              const slowestOps = resultData.performance.slowest_operations || [];
              
              console.log(`⏱️ Total processing time: ${totalTime?.toFixed(2)}s`);
              
              if (slowestOps.length > 0) {
                console.log('🐌 Slowest operations:');
                slowestOps.forEach((op: any, i: number) => {
                  console.log(`   ${i + 1}. ${op.name}: ${op.duration?.toFixed(2)}s (${op.percentage?.toFixed(1)}%)`);
                });
              }
              
              // Check for bottlenecks
              const bottlenecks = resultData.performance.bottlenecks?.bottlenecks || [];
              if (bottlenecks.length > 0) {
                console.warn('⚠️ Performance bottlenecks detected:');
                bottlenecks.forEach((bottleneck: any) => {
                  console.warn(`   - ${bottleneck.operation}: ${bottleneck.duration?.toFixed(2)}s (${bottleneck.percentage?.toFixed(1)}%)`);
                });
              }
            }
            
            // Convert backend results to frontend format
            const vibeAnalysis = resultData.vibe_analysis?.vibe_analysis;
            console.log('Processing vibe analysis:', vibeAnalysis);
            
            if (vibeAnalysis && vibeAnalysis.top_clips && vibeAnalysis.top_clips.length > 0) {
              const convertedClips = vibeAnalysis.top_clips.map((clip: any, index: number) => {
                console.log('Processing clip:', clip);
                return {
                  id: clip.rank || index + 1,
                  name: clip.title || `Clip ${index + 1}`,
                  duration: `0:${Math.floor(clip.duration || 10).toString().padStart(2, '0')}`,
                  thumbnail_url: clip.thumbnail_url || "/api/placeholder/150/100",
                  clip_url: clip.clip_url || clip.url, // Support both clip_url and url
                  startTime: `${Math.floor((clip.start_time || 0) / 60)}:${((clip.start_time || 0) % 60).toFixed(0).padStart(2, '0')}`,
                  endTime: `${Math.floor((clip.end_time || 10) / 60)}:${((clip.end_time || 10) % 60).toFixed(0).padStart(2, '0')}`,
                  confidence: (clip.scores?.overall || 0) / 100,
                  vibe: clip.vibe || 'Unknown',
                  reason: clip.reason || 'Generated clip',
                  scores: clip.scores || {}
                };
              });
              
              console.log('Converted clips:', convertedClips);
              setGeneratedClips(convertedClips);
            } else {
              console.log('No clips found in vibe analysis');
              setGeneratedClips([]);
            }
            
            setIsGenerating(false);
            setShowStatusIndicator(false);
          } else if (statusData.status === 'failed') {
            throw new Error(statusData.error || 'Processing failed');
          } else {
            // Still processing, poll again in 2 seconds
            setTimeout(pollForResults, 2000);
          }
        } catch (error) {
          console.error('Error polling for results:', error);
          setIsGenerating(false);
          setShowStatusIndicator(false);
          alert('Error processing video. Please try again.');
        }
      };
      
      // Start polling
      setTimeout(pollForResults, 2000);
      
    } catch (error) {
      console.error('Error starting clip generation:', error);
      setIsGenerating(false);
      setShowStatusIndicator(false);
      alert('Failed to start clip generation. Please try again.');
    }
  };

  const handleDragStart = (e: React.DragEvent, clip: any) => {
    setDraggedClip(clip);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (draggedClip) {
      setTimelineItems(prev => [...prev, { ...draggedClip, timelineId: Date.now() }]);
      setDraggedClip(null);
    }
  };

  const removeFromTimeline = (timelineId: number) => {
    setTimelineItems(prev => prev.filter(item => item.timelineId !== timelineId));
  };

  const handleSave = async () => {
    setIsSaving(true);
    // Simulate save operation
    setTimeout(() => {
      setIsSaving(false);
      // Show success message or toast
    }, 1000);
  };

  const handleExport = async (platform: string) => {
    setIsExporting(true);
    
    // Simulate export process
    const platformConfig = exportPlatforms.find(p => p.id === platform);
    
    try {
      // This would be where you'd send the timeline clips and BGM to your backend
      console.log(`Exporting for ${platformConfig?.name} with config:`, {
        platform: platform,
        dimensions: platformConfig?.dimensions,
        format: platformConfig?.format,
        timelineClips: timelineItems,
        bgm: selectedBGM?.name,
        projectId: project?.id
      });
      
      // Simulate export processing time
      setTimeout(() => {
        setIsExporting(false);
        setShowExportDialog(false);
        alert(`Export for ${platformConfig?.name} completed! Download will start shortly.`);
      }, 3000);
      
    } catch (error) {
      console.error('Export failed:', error);
      setIsExporting(false);
      alert('Export failed. Please try again.');
    }
  };

  const handleClipClick = (clip: any) => {
    setSelectedClip(clip);
    setShowClipPlayer(true);
  };

  // Handler for BGM dialog selection (preset or upload)
  const handleBgmDialogSelect = (item: { id: string; label: string; type: "bgm"; filename: string }) => {
    setUploadedBgmFilename(item.filename); // For backend
    setAudioItems(prev => [
      ...prev.filter(a => a.type !== 'bgm'),
      { id: 'bgm', label: item.label, type: 'bgm' }
    ]); // For UI, only one BGM
    setShowBgmDialog(false);
  };

  const handleRenderFinalVideo = async () => {
    if (timelineItems.length === 0) {
      alert('Please add clips to the timeline first');
      return;
    }

    setIsRendering(true);
    
    try {
      // Patch: Ensure all timeline items have a valid type and image items have a url
      const patchedTimelineItems = timelineItems.map(item => {
        let patched = { ...item };
        // Always set type
        if (!patched.type) {
          if (patched.clip_url) patched.type = 'clip';
          else if ((patched.url && !patched.clip_url) || (patched.name && patched.name.match(/\.(jpg|jpeg|png|gif)$/i))) patched.type = 'image';
          else if (patched.text) patched.type = 'text';
        }
        // For images, always set url if missing
        if (patched.type === 'image' && !patched.url && patched.name) {
          patched.url = `/assets/images/${patched.name.trim().toLowerCase()}`;
        }
        return patched;
      });
      // Debug: print patched timeline
      console.log('Patched timeline items:', patchedTimelineItems);
      // Compute bgm_regions for image/text segments
      const bgm_regions = computeBgmRegions(patchedTimelineItems);
      // Prepare render request
      // Always use uploadedBgmFilename for backend
      const renderRequest = {
        timeline_clips: patchedTimelineItems,
        project_name: project.name || 'final_video',
        bgm_filename: uploadedBgmFilename || null,
        bgm_regions // <-- NEW: send regions to backend
      };

      console.log('Starting render with data:', renderRequest);

      // Start rendering
      const response = await fetch('http://localhost:8000/api/v1/process/render-timeline', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(renderRequest),
      });

      if (!response.ok) {
        throw new Error(`Render failed: ${response.statusText}`);
      }

      const { job_id } = await response.json();
      setRenderJobId(job_id);

      console.log('Render started, job ID:', job_id);

      // Poll for render status
      const pollRenderStatus = async () => {
        try {
          const statusResponse = await fetch(`http://localhost:8000/api/v1/process/render-status/${job_id}`);
          if (!statusResponse.ok) {
            throw new Error('Failed to get render status');
          }

          const statusData = await statusResponse.json();
          console.log('Render status:', statusData);

          if (statusData.status === 'completed') {
            // Get the final result
            const resultResponse = await fetch(`http://localhost:8000/api/v1/process/render-result/${job_id}`);
            const resultData = await resultResponse.json();

            console.log('Render completed:', resultData);

            // Set the rendered video URL for preview
            setRenderedVideoUrl(resultData.url ? `http://localhost:8000${resultData.url}` : null);
            setIsRendering(false);
            setRenderJobId(null);
            // Optionally show a toast or message: 'Final video rendered!'
            return;
          } else if (statusData.status === 'failed') {
            throw new Error(statusData.error || 'Rendering failed');
          } else {
            // Still rendering, poll again in 2 seconds
            setTimeout(pollRenderStatus, 2000);
          }
        } catch (error) {
          console.error('Error polling render status:', error);
          setIsRendering(false);
          setRenderJobId(null);
          alert('Failed to check render status: ' + error);
        }
      };

      // Start polling
      pollRenderStatus();

    } catch (error) {
      console.error('Error starting render:', error);
      setIsRendering(false);
      alert('Failed to start rendering: ' + error);
    }
  };

  // Helper for status scroll
  const statusSteps = [
    { key: "queued", label: "Queued", icon: AlertTriangle, color: "text-red-500" },
    { key: "rendering", label: "Rendering", icon: Clock, color: "text-yellow-500" },
    { key: "finalizing", label: "Finalizing", icon: Check, color: "text-green-500" },
  ];
  const getCurrentStepIdx = (status: string) => {
    if (status === "queued") return 0;
    if (status === "transcribing" || status === "analyzing") return 1;
    if (status === "finalizing") return 2;
    return 0;
  };
  const currentStepIdx = getCurrentStepIdx(statusState);

  // Add audio to track
  const handleDropAudio = (item: AudioItem) => {
    setAudioItems((prev) => [...prev, item]);
  };
  const handleRemoveAudio = (id: string) => {
    setAudioItems((prev) => prev.filter((item) => item.id !== id));
  };

  // Patch: ensure all timeline items have required fields
  const addToTimeline = (item: any) => {
    if (item.type === 'image') {
      setTimelineItems(prev => [
        ...prev,
        {
          ...item,
          duration: item.duration ? String(item.duration) : '3',
          name: item.name || 'Image',
        }
      ]);
    } else if (item.type === 'text') {
      setTimelineItems(prev => [
        ...prev,
        {
          ...item,
          duration: item.duration ? String(item.duration) : '3',
          name: item.name || 'Text',
          text: item.text || '',
        }
      ]);
    } else if (item.type === 'clip') {
      setTimelineItems(prev => [
        ...prev,
        {
          ...item,
          duration: item.duration ? String(item.duration) : '3',
          name: item.name || 'Clip',
          clip_url: item.clip_url || item.url,
          startTime: item.startTime || '0:00',
          endTime: item.endTime || '0:03',
        }
      ]);
    } else {
      setTimelineItems(prev => [...prev, item]);
    }
  };

  return (
    <div className="p-4 pb-12 flex flex-col gap-4">
      <ProjectHeader project={project} onBack={() => router.push('/projects')} />

      <VibeAgeBadges selectedVibe={selectedVibe} selectedAgeGroup={selectedAgeGroup} vibeColors={vibeColors} ageGroupColors={ageGroupColors} ageGroups={ageGroups} />

      <TopActionRow
        fileInputRef={fileInputRef as React.RefObject<HTMLInputElement>}
        handleVideoSelect={handleVideoSelect}
        handleImportClick={handleImportClick}
        open={open}
        setOpen={setOpen}
        selectedVibe={selectedVibe}
        setSelectedVibe={setSelectedVibe}
        vibes={vibes}
        vibeColors={vibeColors}
        selectedAgeGroup={selectedAgeGroup}
        setSelectedAgeGroup={setSelectedAgeGroup}
        ageGroups={ageGroups}
        addSubtitles={addSubtitles}
        setAddSubtitles={setAddSubtitles}
              />

      <VideoContentCard
        selectedVideo={selectedVideo}
        videoUrl={videoUrl}
        handleRemoveVideo={handleRemoveVideo}
        showStatusIndicator={showStatusIndicator}
        statusState={statusState}
        currentStepIdx={currentStepIdx}
        statusSteps={statusSteps}
        project={project}
        isGenerating={isGenerating}
        handleGenerateClips={handleGenerateClips}
        fastMode={fastMode}
        setFastMode={setFastMode}
        handleTestClips={async () => {
                  try {
                    const response = await fetch('http://localhost:8000/api/v1/process/test-clips');
                    const testData = await response.json();
                    const vibeAnalysis = testData.vibe_analysis?.vibe_analysis;
                    if (vibeAnalysis && vibeAnalysis.top_clips && vibeAnalysis.top_clips.length > 0) {
                      const convertedClips = vibeAnalysis.top_clips.map((clip: any, index: number) => ({
                        id: clip.rank || index + 1,
                        name: clip.title || `Clip ${index + 1}`,
                        duration: `0:${Math.floor(clip.duration || 10).toString().padStart(2, '0')}`,
                        thumbnail_url: clip.thumbnail_url || "/api/placeholder/150/100",
                        clip_url: clip.clip_url || clip.url,
                        startTime: `${Math.floor((clip.start_time || 0) / 60)}:${((clip.start_time || 0) % 60).toFixed(0).padStart(2, '0')}`,
                        endTime: `${Math.floor((clip.end_time || 10) / 60)}:${((clip.end_time || 10) % 60).toFixed(0).padStart(2, '0')}`,
                        confidence: (clip.scores?.overall || 0) / 100,
                        vibe: clip.vibe || 'Unknown',
                        reason: clip.reason || 'Generated clip',
                        scores: clip.scores || {}
                      }));
                      setGeneratedClips(convertedClips);
                      console.log('Test clips loaded:', convertedClips);
                    }
                  } catch (error) {
                    console.error('Error loading test clips:', error);
                  }
                }}
        isImporting={isImporting} // <-- pass loader state
      />

      {/* Editor Space */}
      {selectedVideo && (
        <div className="mt-6 space-y-6">

          <GeneratedClipsCard
            generatedClips={generatedClips}
            isGenerating={isGenerating}
            handleDragStart={handleDragStart}
            handleClipClick={handleClipClick}
            UiverseLoader={UiverseLoader}
            project={project}
          />

          <TimelineEditorCard
            timelineItems={timelineItems}
            setTimelineItems={setTimelineItems}
            imageInputRef={imageInputRef as React.RefObject<HTMLInputElement>}
            handleDrop={handleDrop}
            handleDragOver={handleDragOver}
            audioItems={audioItems}
            handleDropAudio={handleDropAudio}
            handleRemoveAudio={handleRemoveAudio}
            showBgmDialog={showBgmDialog}
            setShowBgmDialog={setShowBgmDialog}
            showSoundEffectsDialog={showSoundEffectsDialog}
            setShowSoundEffectsDialog={setShowSoundEffectsDialog}
            BgmDialog={<BgmDialog open={showBgmDialog} onOpenChange={setShowBgmDialog} onSelect={handleBgmDialogSelect} />}
            SoundEffectsDialog={<SoundEffectsDialog open={showSoundEffectsDialog} onOpenChange={setShowSoundEffectsDialog} onSelect={item => { setAudioItems(prev => [...prev, item]); setShowSoundEffectsDialog(false); }} />}
            handleRenderFinalVideo={handleRenderFinalVideo}
            isRendering={isRendering}
            selectedBGM={selectedBGM}
          />

          {/* Remove the standalone Audio Track Section here */}
                    </div>
      )}

      <ClipPlayerDialog
        showClipPlayer={showClipPlayer}
        setShowClipPlayer={setShowClipPlayer}
        selectedClip={selectedClip}
        setTimelineItems={setTimelineItems}
      />
      <RenderedVideoPreview
        renderedVideoUrl={renderedVideoUrl}
        projectId={projectId}
        onExport={() => router.push(`/projects/${projectId}/export`)}
      />

    </div>
  );
}