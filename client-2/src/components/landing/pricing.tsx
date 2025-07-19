"use client";

import { useRouter } from "next/navigation";
import MistContainer from "../ui/mistcontainer";

// Updated Pricing Card Content
const PriceCardContents = [
  {
    tier: "Indie",
    price: "0",
    subText: "For solo creators and film students",
    btnText: "Start Free",
    onClickHandler: () => {},
    featuresList: [
      { id: 1, content: "Upload up to 5 minutes of footage" },
      { id: 2, content: "Generate 2 audience-specific clips" },
      { id: 3, content: "Basic emotion detection" },
      { id: 4, content: "No watermark for short films" },
    ],
  },
  {
    tier: "Studio",
    price: "15",
    subText: "For small teams & YouTube filmmakers",
    btnText: "Get Studio Access",
    onClickHandler: () => {},
    featuresList: [
      { id: 1, content: "Up to 60 minutes of footage/month" },
      { id: 2, content: "Generate unlimited personalized clips" },
      { id: 3, content: "AI-powered emotion timeline" },
      { id: 4, content: "Platform-ready (Reels, Shorts, Status)" },
    ],
  },
  {
    tier: "Pro",
    price: "49",
    subText: "For filmmakers & production houses",
    btnText: "Go Pro",
    onClickHandler: () => {},
    featuresList: [
      { id: 1, content: "120+ minutes of footage/month" },
      { id: 2, content: "Advanced voiceover & dubbing (coming soon)" },
      { id: 3, content: "Engagement scoring & targeting" },
      { id: 4, content: "Early access to timeline editor & beta tools" },
    ],
  },
];

export default function Pricing() {
  return (
    <div
      id="pricing"
      className="px-4 sm:px-6 md:px-10 lg:px-20 xl:px-28 2xl:px-40 xl:py-10"
    >
      <div>
        <p className="text-xl md:text-3xl lg:text-4xl xl:text-6xl font-medium pb-3">
          Choose the right cut for your crew
        </p>
        <p className="text-xs md:text-[16px] lg:text-lg text-[#A8A8A8] max-w-3xl w-[70%] lg:w-[45%] xl:w-[60%]">
          Whether you’re a solo creator or a full production team, generate and
          share audience-specific movie promos with GenAI—fast, smart, and
          personal.
        </p>
      </div>

      {/* Pricing container */}
      <MistContainer className="mt-5 mb-10 border border-[#565555] rounded-3xl relative overflow-hidden">
        {/* Violet gradient background */}
        <img
          src="/assets/bg/violet-gradient-bg.jpg"
          alt="Violet Gradient Background"
          className="absolute inset-0 w-full h-full object-cover opacity-60 blur-md z-0 pointer-events-none select-none"
        />
        <div className="relative z-10 p-4 lg:p-5 grid grid-cols-1 md:grid-cols-3 h-full gap-x-4 lg:gap-x-5 gap-y-4 md:gap-y-0">
          {PriceCardContents.map((elem, key) => {
            return (
              <PriceCard
                key={key}
                tier={elem.tier}
                price={elem.price}
                subText={elem.subText}
                btnText={elem.btnText}
                featuresList={elem.featuresList}
                onClickHandler={elem.onClickHandler}
              />
            );
          })}
        </div>
      </MistContainer>
    </div>
  );
}

const ProClass =
  "rounded-xl p-4 h-full bg-[rgba(0,0,0,0.4)] backdrop-blur-lg border-1 border-[#565555]";

const PriceCard = ({
  tier,
  price,
  subText,
  btnText,
  featuresList,
  onClickHandler,
}: {
  tier: string;
  price: string;
  subText: string;
  btnText: string;
  featuresList: { id: number; content: string }[];
  onClickHandler: () => void;
}) => {
  const router = useRouter();

  return (
    <div
      className={
        tier === "Pro"
          ? ProClass
          : "rounded-xl p-4 h-full bg-[rgba(0,0,0,0.4)] backdrop-blur-lg"
      }
    >
      <p className="text-lg font-semibold">{tier}</p>

      <span className="flex items-baseline mt-4 mb-10">
        <p className="text-4xl font-medium">${price}</p>
        <p className="ml-1 text-sm text-[#999]">/month</p>
      </span>

      <span className="flex mb-4 text-[#c1c1c1]">{subText}</span>

      <button
        onClick={onClickHandler}
        className={`h-10 md:text-sm lg:text-[16px] rounded-xl w-full mb-4 border ${
          tier === "Pro"
            ? "bg-[#565555] border-[#7d8483] hover:bg-[#383737]"
            : "bg-[#2A2A2C] border-[0.3px] border-[#565555] hover:bg-[#383737]"
        } cursor-pointer transition-all duration-300`}
      >
        {btnText}
      </button>

      <div className="flex items-center gap-x-4 text-sm lg:text-[16px] mb-2 text-[#a8a8a8]">
        <div className="border border-[#565555] bg-[#565555] w-2 h-2 rounded-full"></div>
        <div className="border-b border-[#565555] flex-1 h-0.5"></div>
        <p>Features</p>
        <div className="border-b border-[#565555] flex-1 h-0.5"></div>
        <div className="border border-[#565555] bg-[#565555] w-2 h-2 rounded-full"></div>
      </div>

      <ul className="flex flex-col gap-y-3 mt-4 text-sm lg:text-[16px] text-[#a7b0b3]">
        {featuresList.map((elem) => (
          <li
            key={elem.id}
            className="flex items-center gap-x-2 hover:text-white transition-all duration-200"
          >
            <p>✔︎</p>
            <p>{elem.content}</p>
          </li>
        ))}
      </ul>
    </div>
  );
};
