
export default function Footer() {
  return (
    <div className="px-4 sm:px-6 md:px-10 lg:px-14 xl:px-28 2xl:px-40 border-t-[0.5px] border-[#565555]">
      {/* Top Section */}
      <div className="flex items-center justify-between border-b-[0.5px] border-[#565555] h-24 md:h-40">
        <div className="flex items-center gap-x-2 lg:gap-x-4">
          <div className="w-5 sm:w-6 md:w-8 lg:w-10 xl:w-12 h-5 sm:h-6 md:h-8 lg:h-10 xl:h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-xs sm:text-sm md:text-base lg:text-lg xl:text-xl">C</span>
          </div>
          <p className="text-[16px] sm:text-xl md:text-2xl lg:text-3xl xl:text-4xl">
            ClipCraft
          </p>
        </div>
        <p className="text-[14px] sm:text-xl md:text-2xl lg:text-3xl xl:text-4xl text-right">
          Cut once. Connect forever.
        </p>
      </div>

      {/* Middle Grid */}
      <div className="grid grid-cols-2 gap-y-10 md:gap-y-0 md:grid-cols-4 py-10">
        <div className="col-span-1">
          <p className="text-[14px] lg:text-[16px] lg:text-xl font-bold">Features</p>
          <ul className="flex flex-col mt-8 gap-y-4 text-[14px] lg:text-[16px] text-[#c9c9cc]">
            <li>Smart Clip Generator</li>
            <li>Audience Targeting</li>
            <li>Auto Captioning</li>
          </ul>
        </div>

        <div className="col-span-1">
          <p className="text-[14px] lg:text-[16px] lg:text-xl font-bold">Product</p>
          <ul className="flex flex-col mt-8 gap-y-4 text-[14px] lg:text-[16px] text-[#c9c9cc]">
            <li>ClipCraft Studio</li>
            <li>Editor Preview Mode</li>
            <li>Reel Formatter</li>
          </ul>
        </div>

        <div className="col-span-1">
          <p className="text-[14px] lg:text-[16px] lg:text-xl font-bold">Resources</p>
          <ul className="flex flex-col mt-8 gap-y-4 text-[14px] lg:text-[16px] text-[#c9c9cc]">
            <li>Hackathon Build Docs</li>
            <li>How it Works</li>
            <li>Demo Video (Coming Soon)</li>
          </ul>
        </div>

        <div className="col-span-1">
          <p className="text-[14px] lg:text-[16px] lg:text-xl font-bold">Connect With Us</p>
          <ul className="flex flex-col mt-8 gap-y-4 text-[#c9c9cc]">
            <li>X (Demo)</li>
            <li>GitHub (Private)</li>
            <li>LinkedIn (Not Live)</li>
          </ul>
        </div>
      </div>

      {/* Bottom Strip */}
      <div className="border-t-[0.5px] border-[#565555] h-20 flex items-center justify-between font-extralight text-[#827d7d] text-[12px] sm:text-[13px] lg:text-sm">
        <p className="cursor-default">
          &copy; 2025 ClipCraft | Built by team APX
        </p>
        <div className="flex items-center gap-x-2 sm:gap-x-4 lg:gap-x-8">
          <span className="cursor-default">Terms</span>
          <span className="cursor-default">Privacy</span>
          <span className="cursor-default">About</span>
        </div>
      </div>
    </div>
  );
}
