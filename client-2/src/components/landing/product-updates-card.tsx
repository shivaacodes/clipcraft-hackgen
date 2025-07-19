"use client";

import { Icons } from "@/components/icons";
import { useState } from "react";

export const UpdatesCard = () => {
  const [hoveredOn, setHoveredOn] = useState<
    "editing" | "rendering" | "queued" | "nothing"
  >("nothing");

  return (
    <div className="flex flex-col h-full w-full">
      <p className="text-xl font-medium mt-10">ClipCraft progress updates</p>
      <p className="mt-2 text-[16px] text-[#A8A8A8] w-[90%] xl:w-[80%]">
        See how your clip generation is progressing — from scene selection to final export.
      </p>

      <div className="relative mt-8 md:mt-0 w-full md:w-[90%] flex flex-col items-center justify-center md:h-[340px] h-[300px]">
        {/* Card 3 - QUEUED */}
        <div
          onMouseEnter={() => setHoveredOn("queued")}
          onMouseLeave={() => setHoveredOn("nothing")}
          className="z-10 h-48 p-4 rounded-2xl border border-[#2d2d2f] bg-[#1c1e1f] backdrop-blur-lg text-white
          hover:bg-[#2a2c2e] transition-all duration-300 hover:-translate-y-5
          shadow-[inset_-12px_-18px_74px_0_rgba(0,0,0,0.28)] cursor-pointer
          mb-4 md:mb-0 absolute bottom-20 left-0 right-0"
        >
          <div
            className={`font-medium flex items-center gap-1 transition-all duration-300 ${
              hoveredOn === "queued" ? "text-[#f21c1c]" : "text-[#8f9191]"
            }`}
          >
            {hoveredOn === "queued" ? (
              <Icons.CrossRed className="flex w-5" />
            ) : (
              <Icons.CrossMono className="flex w-5" />
            )}
            <span>Queued</span>
          </div>
          <p className="mt-5 text-2xl">Footage uploaded — awaiting processing</p>
          <div className="absolute bottom-2 text-lg text-[#A8A8A8]">Jul 8</div>
        </div>

        {/* Card 2 - RENDERING */}
        <div
          onMouseEnter={() => setHoveredOn("rendering")}
          onMouseLeave={() => setHoveredOn("nothing")}
          className="z-20 h-48 p-4 rounded-2xl border border-[#2d2d2f] bg-[#1c1e1f] backdrop-blur-lg text-white
          hover:bg-[#2a2c2e] transition-all duration-300 hover:-translate-y-5
          shadow-[inset_-12px_-18px_74px_0_rgba(0,0,0,0.28)] cursor-pointer
          mb-4 md:mb-0 absolute bottom-10 left-0 right-0"
        >
          <div
            className={`font-medium flex items-center gap-1 transition-all duration-300 ${
              hoveredOn === "rendering" ? "text-[#ebe839]" : "text-[#8f9191]"
            }`}
          >
            {hoveredOn === "rendering" ? (
              <Icons.DelayedYellow className="flex w-5" />
            ) : (
              <Icons.DelayedMono className="flex w-5" />
            )}
            <span>Rendering</span>
          </div>
          <p className="mt-5 text-2xl">Clips being stitched with vibe-matched BGM</p>
          <div className="absolute bottom-2 text-lg text-[#A8A8A8]">Jul 9</div>
        </div>

        {/* Card 1 - EDITING */}
        <div
          onMouseEnter={() => setHoveredOn("editing")}
          onMouseLeave={() => setHoveredOn("nothing")}
          className="z-30 h-48 p-4 rounded-2xl border border-[#2d2d2f] bg-[#1c1e1f] backdrop-blur-lg text-white
          hover:bg-[#2a2c2e] transition-all duration-300 hover:-translate-y-5
          shadow-[inset_-12px_-18px_74px_0_rgba(0,0,0,0.28)] cursor-pointer
          absolute bottom-0 left-0 right-0"
        >
          <div
            className={`font-medium flex items-center gap-1 transition-all duration-300 ${
              hoveredOn === "editing" ? "text-[#39eb5f]" : "text-[#8f9191]"
            }`}
          >
            {hoveredOn === "editing" ? (
              <Icons.OnTrackGreen className="flex w-5" />
            ) : (
              <Icons.OnTrackMono className="flex w-5" />
            )}
            <span>Finalizing</span>
          </div>
          <p className="mt-5 text-2xl">Preview ready — editor can now fine-tune scenes</p>
          <div className="absolute bottom-2 text-lg text-[#A8A8A8]">Jul 10</div>
        </div>
      </div>
    </div>
  );
};
