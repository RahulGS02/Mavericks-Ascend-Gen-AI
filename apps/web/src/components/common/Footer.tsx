export default function Footer() {
  return (
    <footer className="bg-white border-t border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex justify-center items-center">
          <div className="text-sm text-gray-600">
            Copyright © {new Date().getFullYear()} Mavericks. All Rights Reserved.
          </div>
        </div>
      </div>
    </footer>
  );
}
