import Link from 'next/link';

export default function Header() {
  return (
    <header className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-20">
          {/* Logo */}
          <Link href="/">
            <h1 className="text-2xl font-black text-blue-900 tracking-tight uppercase cursor-pointer hover:text-blue-800 transition-colors">
              MAVERICKS ASCEND
            </h1>
          </Link>

          {/* Navigation */}
          <nav className="flex items-center space-x-4">
            <Link
              href="/login"
              className="px-6 py-2.5 bg-blue-900 text-white text-sm font-bold uppercase tracking-wide rounded hover:bg-blue-800 transition-colors"
            >
              SIGN IN
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
}
