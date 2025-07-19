"use client";

import Image from "next/image";
import { BlurFade } from "../magicui/blur-fade";
import { motion } from "framer-motion";

export default function Hero() {
  return (
    <div>
      <div className="relative flex flex-col justify-center items-center px-4 sm:px-6 md:px-10 lg:px-14 xl:px-28 2xl:px-40 pt-16 sm:pt-20 md:pt-24 lg:pt-32 xl:pt-36">
        {/* CSS Grid Pattern Background */}
        <div
          className="absolute inset-0 opacity-20 z-0"
          style={{
            backgroundImage: `
              linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px),
              linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)
            `,
            backgroundSize: "40px 40px",
          }}
        />

        <div className="relative z-10 flex flex-col items-center text-center">
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-extrabold tracking-tight leading-tight text-white"
          >
            Every story has many faces
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="mt-2 flex flex-wrap justify-center items-center gap-x-1 xl:gap-x-3 text-2xl sm:text-3xl md:text-4xl lg:text-5xl xl:text-6xl font-bold"
          >
            <p className="text-transparent bg-gradient-to-b from-gray-400 via-gray-200 to-white bg-clip-text">
              We help you show the right one
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.5 }}
            className="mt-6 flex flex-col items-center font-extralight text-[#AEAEAE] text-sm sm:text-base md:text-lg lg:text-xl xl:text-2xl"
          >
            <p>Designed for storytellers in the GenAI era.</p>
            <p>Turn raw footage into custom reels that speak to every kind of viewer.</p>
          </motion.div>
        </div>
      </div>

      <HomeBanner />
    </div>
  );
}

const HomeBanner = () => {
  return (
    <BlurFade
      delay={1}
      inView
      className="px-4 sm:px-6 md:px-10 lg:px-14 xl:px-28 2xl:px-40 mt-12 sm:mt-16"
    >
      <div className="flex justify-center border border-[#313032] rounded-2xl p-1 md:p-2 bg-[#16161681] h-[600px] sm:h-[650px] md:h-[700px]">
        <Image
          className="rounded-[11px] border border-[#515252] w-full h-full object-cover"
          src="/assets/bg/dashboard.png"
          alt="Dashboard Banner"
          width={1600}
          height={700}
        />
      </div>
    </BlurFade>
  );
};
