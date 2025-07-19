import GoBackBtn from "./gohome-button";

export default function NotFoundPage() {
  return (
    <div className="relative h-screen w-screen flex items-center justify-center overflow-hidden">
      {/* Blurred Background Image */}
      <div className="absolute inset-0 -z-10 bg-gradient-to-br from-gray-800 to-gray-900" />

      {/* main content */}
      <div className="relative z-10 flex flex-col items-center">
        <p className="text-6xl md:text-7xl lg:text-8xl font-bold text-white drop-shadow-lg">
          404
        </p>
        <p className="text-2xl text-white mt-4 drop-shadow-md">
          Page Not Found
        </p>
        <p className="mt-1 text-[#b8bdc2] text-[13px] sm:text-[16px] font-extralight">
          Oops! The page you&apos;re looking for doesn&apos;t exist or has been
          moved.
        </p>

        <GoBackBtn />
      </div>
    </div>
  );
}
