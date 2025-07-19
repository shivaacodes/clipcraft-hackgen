import React, { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Mic, Send } from "lucide-react";

interface FindInputProps {
  onSubmit: (input: string, isVoice: boolean, language: string) => void;
  isLoading?: boolean;
}

const FindInput: React.FC<FindInputProps> = ({ onSubmit, isLoading }) => {
  const [input, setInput] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [language, setLanguage] = useState("en");
  const recognitionRef = useRef<any>(null);

  const handleRecord = () => {
    if (!isRecording) {
      if (typeof window !== "undefined") {
        const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
        if (SpeechRecognition) {
          const recognition = new SpeechRecognition();
          recognition.lang = language === "ml" ? "ml-IN" : "en-US";
          recognition.interimResults = false;
          recognition.maxAlternatives = 1;
          recognition.onresult = (event: any) => {
            const transcript = event.results[0][0].transcript;
            setInput(transcript);
          };
          recognition.onend = () => {
            setIsRecording(false);
          };
          recognition.onerror = () => {
            setIsRecording(false);
          };
          recognitionRef.current = recognition;
          recognition.start();
          setIsRecording(true);
        } else {
          alert("Speech recognition is not supported in this browser.");
        }
      }
    } else {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
        setIsRecording(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) {
      onSubmit(input, false, language);
      // Do not clear the input after submit
      // setInput("");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row items-center gap-3 w-full p-5 bg-card rounded-2xl shadow-lg border border-muted-foreground/10">
      <select
        className="mb-2 sm:mb-0 px-3 py-2 rounded-lg border border-muted-foreground/20 text-base focus:outline-none focus:ring-2 focus:ring-primary/30 bg-background"
        value={language}
        onChange={e => setLanguage(e.target.value)}
        disabled={isLoading || isRecording}
        style={{ minWidth: 120 }}
      >
        <option value="en">English</option>
        <option value="ml">Malayalam</option>
      </select>
      <input
        type="text"
        className="flex-1 px-5 py-3 border border-muted-foreground/20 rounded-2xl text-lg focus:outline-none focus:ring-2 focus:ring-primary/30 transition-all bg-background shadow-sm"
        placeholder="Type what you want to find..."
        value={input}
        onChange={(e) => setInput(e.target.value)}
        disabled={isLoading || isRecording}
      />
      <div className="flex gap-2 w-full sm:w-auto">
        <Button type="button" onClick={handleRecord} disabled={isLoading} className={`flex-1 sm:flex-none px-5 py-3 rounded-xl text-base font-semibold transition-all ${isRecording ? "bg-red-600 text-white" : ""}`}>
          <Mic className="w-5 h-5 mr-2" />
        {isRecording ? "Stop" : "Record"}
      </Button>
        <Button type="submit" disabled={isLoading || isRecording || !input.trim()} className="flex-1 sm:flex-none px-5 py-3 rounded-xl text-base font-semibold transition-all">
          <Send className="w-5 h-5 mr-2" />
          Search
      </Button>
      </div>
    </form>
  );
};

export default FindInput; 