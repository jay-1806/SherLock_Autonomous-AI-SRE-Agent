export default function NotFound() {
  return (
    <div className="text-center py-12">
      <h1 className="text-4xl font-bold text-gray-900 mb-4">404</h1>
      <p className="text-gray-600 mb-6">Investigation not found</p>
      <a href="/" className="text-indigo-600 hover:text-indigo-800">
        ← Back to Investigations
      </a>
    </div>
  );
}
