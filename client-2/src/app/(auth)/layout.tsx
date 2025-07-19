export default function AuthLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <div className="flex items-center justify-between h-screen">
            <div className="hidden lg:block lg:w-1/2 h-full bg-gradient-to-br from-gray-900 via-black to-gray-800">
                <div className="w-full h-full flex items-center justify-center">
                    <div className="text-center">
                        <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-6">
                            <span className="text-white font-bold text-3xl">C</span>
                        </div>
                        <h1 className="text-white text-3xl font-bold mb-2">ClipCraft</h1>
                        <p className="text-gray-400 text-lg">Every story has many faces</p>
                        <p className="text-gray-500 text-sm mt-2">We help you show the right one</p>
                    </div>
                </div>
            </div>
            <div className="w-full lg:w-1/2 h-full flex items-center justify-center px-2 md:px-0">
                {children}
            </div>
        </div>
    );
}