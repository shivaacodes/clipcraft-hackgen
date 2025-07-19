"use client";

import Image from "next/image";
import Link from "next/link";
import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { useSession, signOut } from "@/utils/auth";
import { usePathname } from "next/navigation";
import { Icons } from "@/components/icons";
import { toast } from "sonner";
import { createPortal } from "react-dom";

const optionsArr: {
  title: string;
  href: string;
  openToNewPage: boolean;
}[] = [
  {
    title: "Profile",
    href: "/profile",
    openToNewPage: false,
  },
  {
    title: "Search for help…",
    href: "",
    openToNewPage: false,
  },
  {
    title: "Shortcuts",
    href: "",
    openToNewPage: false,
  },
  { title: "Docs", href: "", openToNewPage: true },
  {
    title: "Contact us",
    href: "",
    openToNewPage: false,
  },
  {
    title: "Community",
    href: "",
    openToNewPage: true,
  },
];

const navListArr = [
  { title: "Features", redirectHref: "#features" },
  { title: "Pricing", redirectHref: "#pricing" },
  { title: "About", redirectHref: "#about" },
  { title: "Contact", redirectHref: "#contact" },
];

const itemVariants = {
  open: {
    opacity: 1,
    y: 0,
    transition: {
      when: "beforeChildren",
    },
  },
  closed: {
    opacity: 0,
    y: -15,
    transition: {
      when: "afterChildren",
    },
  },
};

const wrapperVariants = {
  open: {
    scaleY: 1,
    opacity: 1,
    transition: {
      when: "beforeChildren",
      staggerChildren: 0.1,
    },
  },
  closed: {
    scaleY: 0,
    opacity: 0,
    transition: {
      when: "afterChildren",
      staggerChildren: 0.1,
    },
  },
};


export default function Navbar() {
  const { data: session, isPending } = useSession();
  const [signupLoading, setSignupLoading] = useState(false);
  const pathname = usePathname();

  const [isOpen, setIsOpen] = useState(false);
  const [profileTabOpen, setProfileTabOpen] = useState(false);
  const [showNavbar, setShowNavbar] = useState(true);
  const [lastScrollY, setLastScrollY] = useState(0);

  const handleSignout = () => {
    try {
      setSignupLoading(true);
      signOut();
    } catch (error) {
      toast.error("Error occurred while signing out.");
    } finally {
      setSignupLoading(false);
      toast.success("Logged out successfully!");
    }
  };

  useEffect(() => {
    const handleScroll = () => {
      const currentY = window.scrollY;
      if (currentY > lastScrollY && currentY > 50) {
        setShowNavbar(false);
      } else {
        setShowNavbar(true);
      }
      setLastScrollY(currentY);
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, [lastScrollY]);

  return (
    <>
      <div
        className={`top-0 fixed w-full py-2 flex justify-center px-4 sm:px-6 md:px-10 lg:px-20 xl:px-28 2xl:px-40 z-50 transition-transform duration-300 ${showNavbar ? "translate-y-0" : "-translate-y-full"}`}
      >
        <div className="h-[60px] border border-[#313032]/50 w-full max-w-6xl rounded-2xl flex items-center justify-between bg-black/80 backdrop-blur-md shadow-lg relative mx-auto">
          {/* Logo */}
          <div className="flex items-center gap-x-3 ml-4">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">C</span>
            </div>
            <span className="font-bold text-lg bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">ClipCraft</span>
          </div>

          {/* Nav links - centered */}
          <div className="hidden md:flex gap-x-8 lg:gap-x-12 xl:gap-x-16 absolute left-1/2 transform -translate-x-1/2">
            {navListArr.map((elem, key) => (
              <NavListElement
                title={elem.title}
                key={key}
                redirectHref={elem.redirectHref}
              />
            ))}
          </div>

          {/* Right buttons */}
          <div className="hidden md:flex items-center gap-x-2 mr-3 min-w-[120px] justify-end relative">
            {isPending && (
              <div className="w-24 h-9 flex items-center justify-center animate-pulse bg-gray-800 rounded-md" />
            )}
            {!isPending && !session?.user?.id &&
              pathname !== "/login" &&
              pathname !== "/sign-in" && (
                <Link
                  href="/sign-in"
                  className="bg-white text-black px-5 py-[6px] text-sm rounded-md hover:bg-gray-100 transition-all duration-300 shadow-sm border border-gray-200 font-medium"
                >
                  Sign in
                </Link>
              )}

            {!isPending && session?.user?.email && (
              <button
                aria-label="Toggle menu"
                aria-expanded={profileTabOpen}
                onClick={() => setProfileTabOpen(!profileTabOpen)}
                className="flex flex-col justify-center items-center w-9 h-9 border border-[#313032] rounded-lg bg-[#38373771] cursor-pointer"
                type="button"
              >
                <span className={`block h-0.5 w-6 bg-[#959292] rounded transition-all duration-300 ${profileTabOpen ? "rotate-45 translate-y-2" : ""}`} />
                <span className={`block h-0.5 w-6 bg-[#959292] rounded transition-all duration-300 my-1 ${profileTabOpen ? "opacity-0" : ""}`} />
                <span className={`block h-0.5 w-6 bg-[#959292] rounded transition-all duration-300 ${profileTabOpen ? "-rotate-45 -translate-y-2" : ""}`} />
              </button>
            )}

            {/* Profile dropdown - use portal or fixed positioning */}
            {profileTabOpen && !isPending && (
              typeof window !== "undefined"
                ? createPortal(
                    <div className="fixed top-[70px] right-10 w-56 bg-[rgba(0,0,0,0.95)] backdrop-blur-lg border border-[#414141] rounded-xl shadow-2xl p-1 z-[9999] animate-in fade-in">
                {optionsArr.map((elem, key) => (
                  <div key={key} className="px-3 py-2 hover:bg-[#3d3d3e80] transition-all duration-300 rounded-md cursor-pointer">
                    {elem.href ? (
                      <Link
                        href={elem.href}
                        className="text-sm text-white"
                        target={elem.openToNewPage ? "_blank" : "_self"}
                      >
                        {elem.title}
                      </Link>
                    ) : (
                      <span className="text-sm text-white">{elem.title}</span>
                    )}
                  </div>
                ))}
                <div
                  className="px-3 py-2 hover:bg-[#3d3d3e80] transition-all duration-300 rounded-md cursor-pointer"
                  onClick={handleSignout}
                >
                  <span className="text-sm text-white">Logout</span>
                </div>
                    </div>,
                    document.body
                  )
                : null
            )}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex gap-x-[5px]">
            <Link
              href="https://github.com/kartikver15gr8/zenorizon"
              target="_blank"
              className="border border-[#313032] flex items-center gap-x-1 h-9 px-2 rounded-lg bg-black text-[13px]"
            >
              <Icons.Github className="w-3" />
              <p>Star on GitHub</p>
              <span className="text-yellow-400">★</span>
            </Link>
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="flex flex-col justify-center items-center w-9 h-9 border border-[#313032] rounded-lg bg-[#38373771] cursor-pointer"
              type="button"
            >
              <span className={`block h-0.5 w-6 bg-[#959292] rounded transition-all duration-300 ${isOpen ? "rotate-45 translate-y-2" : ""}`} />
              <span className={`block h-0.5 w-6 bg-[#959292] rounded transition-all duration-300 my-1 ${isOpen ? "opacity-0" : ""}`} />
              <span className={`block h-0.5 w-6 bg-[#959292] rounded transition-all duration-300 ${isOpen ? "-rotate-45 -translate-y-2" : ""}`} />
            </button>
          </div>
        </div>
      </div>

      {/* Mobile nav dropdown */}
      {isOpen && (
        <div className="fixed mt-[70px] rounded px-4 w-full z-50">
          <motion.div
            className="relative w-full border border-[#313032] bg-[#121212] shadow-lg rounded-lg"
            initial="closed"
            animate="open"
            variants={wrapperVariants}
          >
            <div className="text-white font-medium flex flex-col shadow-[inset_5px_2px_30px_rgba(0,0,0,0.1)]">
              {navListArr.map((elem, key) => (
                <NavLink
                  key={key}
                  href={elem.redirectHref}
                  text={elem.title}
                  isOpen={isOpen}
                  setIsOpen={setIsOpen}
                />
              ))}
              <motion.div variants={itemVariants}>
                {session?.user?.email ? (
                  <div
                    className="h-16 flex items-center hover:bg-[#3d3d3e80] transition-all duration-500 px-5 py-2 hover:rounded-md"
                    onClick={() => {
                      handleSignout();
                      setIsOpen(false);
                    }}
                  >
                    Log out
                  </div>
                ) : (
                  <Link
                    href="/sign-in"
                    className="h-16 flex items-center bg-white text-black hover:bg-gray-100 transition-all duration-500 px-5 py-2 rounded-md mx-2 mb-2 font-semibold shadow-sm"
                    onClick={() => setIsOpen(false)}
                  >
                    Sign in
                  </Link>
                )}
              </motion.div>
            </div>
          </motion.div>
        </div>
      )}
    </>
  );
}


const NavListElement = ({
  title,
  className,
  redirectHref,
  onClickHandler,
}: {
  title: string;
  className?: string;
  redirectHref: string;
  onClickHandler?: () => void;
}) => {
  return onClickHandler ? (
    <p
      onClick={onClickHandler}
      className={`${className} text-[14px] lg:text-[16px] font-medium rounded-lg px-3 py-2 hover:text-white hover:bg-white/10 transition-all duration-300 cursor-pointer text-gray-200`}
    >
      {title}
    </p>
  ) : (
    <Link
      href={redirectHref}
      className={`${className} text-[14px] lg:text-[16px] font-medium rounded-lg px-3 py-2 hover:text-white hover:bg-white/10 transition-all duration-300 cursor-pointer text-gray-200`}
    >
      {title}
    </Link>
  );
};

const NavLink = ({
  href,
  text,
  isOpen,
  setIsOpen,
  onClickHandler,
}: {
  href: string;
  text: string;
  isOpen: boolean;
  setIsOpen: React.Dispatch<React.SetStateAction<boolean>>;
  onClickHandler?: () => void;
}) => (
  <motion.div variants={itemVariants}>
    {onClickHandler ? (
      <div
        className="h-16 flex items-center hover:bg-[#3d3d3e80] transition-all duration-500 px-5 py-2 hover:rounded-md border-b border-[#313032]"
        onClick={() => {
          onClickHandler();
          setIsOpen(!isOpen);
        }}
      >
        {text}
      </div>
    ) : (
      <Link
        href={href}
        className="h-16 flex items-center hover:bg-[#3d3d3e80] transition-all duration-500 px-5 py-2 hover:rounded-md border-b border-[#313032]"
        onClick={() => {
          setIsOpen(!isOpen);
        }}
      >
        {text}
      </Link>
    )}
  </motion.div>
);
