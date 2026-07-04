import DocumentList from "@/components/DocumentList";
import UploadZone from "@/components/UploadZone";

export default function Home() {
  return (
    <div className="h-full overflow-auto px-8 py-6 space-y-6 max-w-3xl">
      <UploadZone />
      <DocumentList />
    </div>
  );
}
