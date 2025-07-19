import { UpdatesCard } from "./product-updates-card";

export default function ProductTimeline() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-[#151515] via-[#0f1011] to-[#0A0A0A] px-4 sm:px-6 md:px-10 lg:px-14 xl:px-28 2xl:px-40 gap-y-3 sm:gap-y-4 md:gap-y-5 xl:gap-y-6 py-5 lg:py-10 xl:pb-20">
      <div className="mb-4 md:mb-8">
        <div className="flex items-center gap-x-2 text-xs md:text-sm lg:text-lg">
          <p>One platform. Smarter storytelling.</p>
          <div className="w-3 h-3 md:w-4 md:h-4 rotate-45 rounded shadow-[inset_-3px_-0.1px_7px_2px_rgba(255,255,255,0.4)] border border-[#717171]"></div>
        </div>
        <p className="text-xl md:text-3xl lg:text-4xl xl:text-6xl font-medium pb-3 pt-2 md:pb-5 md:pt-3">
          From raw footage to reel-ready
        </p>
        <p className="text-xs md:text-[16px] lg:text-lg text-[#A8A8A8] max-w-3xl w-[70%] lg:w-[45%]">
          ClipCraft helps you organize, cut, and export short promos from film content —
          optimized for audience mood, genre, and platform format.
        </p>
      </div>

      <div className="mb-10">
        <div className="w-full h-64 bg-gradient-to-br from-purple-900/20 to-fuchsia-900/20 opacity-65 rounded-lg border border-[#313032] flex items-center justify-center">
          <p className="text-gray-400">Audience Map / Clip Graph Placeholder</p>
        </div>
      </div>

      <div className="border-t border-[#2f2f2f] mt-5 grid grid-cols-1 md:grid-cols-2 gap-6">
        <TimelineCard />
        <UpdatesCard />
      </div>
    </div>
  );
}

const TimelineCard = () => {
  return (
    <div className="relative">
      <div className="md:border-r border-[#555555] pt-10">
        <p className="text-xl font-medium">Track clip generation flow</p>
        <p className="mt-2 text-[16px] text-[#A8A8A8] w-[90%] xl:w-[80%]">
          See how your clips are generated — from script analysis to vibe detection,
          scene selection, and final export. All in one intuitive timeline.
        </p>
        <div className="border border-[#2d2e2e] rounded-2xl p-2 mt-7">
          <div className="w-full h-48 bg-gradient-to-br from-gray-800 to-gray-900 border border-[#515252] rounded-[10px] flex items-center justify-center overflow-hidden">
            <img
              src="/assets/bg/timeline.png"
              alt="Clip Timeline"
              className="object-contain w-full h-full"
            />
          </div>
        </div>
      </div>

      <div className="absolute shadow-[inset_-40px_-91px_136px_0px_#0A0A0A] top-0 w-full h-full"></div>
    </div>
  );
};
