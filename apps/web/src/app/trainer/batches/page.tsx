"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { BookOpen, Search, Calendar, Users, TrendingUp, ArrowRight, Filter } from "lucide-react";
import { apiClient } from "@/lib/api/client";
import { toast } from "sonner";
import DashboardLayout from "@/components/DashboardLayout";

interface Batch {
  id: string;
  name: string;
  description?: string;
  pipeline_name: string;
  status: string;
  start_date: string;
  end_date: string;
  current_enrollment: number;
  max_capacity: number;
  average_progress: number;
  category?: string;
}

export default function TrainerBatchesPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [batches, setBatches] = useState<Batch[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");

  useEffect(() => {
    fetchBatches();
  }, [statusFilter]);

  const fetchBatches = async () => {
    try {
      setLoading(true);
      const params: any = {};
      if (statusFilter !== "all") {
        params.status_filter = statusFilter.toUpperCase();
      }
      const response = await apiClient.get("/trainer/dashboard/batches", { params });
      setBatches(response.data.batches || []);
    } catch (error) {
      console.error("Failed to fetch batches:", error);
      toast.error("Failed to load batches");
    } finally {
      setLoading(false);
    }
  };

  const filteredBatches = batches.filter((batch) =>
    batch.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    batch.pipeline_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getStatusColor = (status: string) => {
    switch (status.toUpperCase()) {
      case "ACTIVE":
        return "bg-green-100 text-green-800 border-green-300";
      case "COMPLETED":
        return "bg-blue-100 text-blue-800 border-blue-300";
      case "PLANNED":
        return "bg-yellow-100 text-yellow-800 border-yellow-300";
      default:
        return "bg-gray-100 text-gray-800 border-gray-300";
    }
  };

  return (
    <DashboardLayout>
      <div className="p-6 max-w-7xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">My Batches</h1>
          <p className="text-gray-600">All training batches assigned to you</p>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Search batches..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Filter className="w-5 h-5 text-gray-400" />
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">All Status</option>
                <option value="active">Active</option>
                <option value="completed">Completed</option>
                <option value="planned">Planned</option>
              </select>
            </div>
          </div>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-gray-300 border-t-blue-600"></div>
            <p className="mt-4 text-gray-600">Loading batches...</p>
          </div>
        ) : filteredBatches.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
            <BookOpen className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No batches found</h3>
            <p className="text-gray-600">
              {searchTerm ? "Try adjusting your search terms" : "No batches have been assigned to you yet"}
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredBatches.map((batch) => (
              <button
                key={batch.id}
                onClick={() => router.push(`/batches/${batch.id}`)}
                className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 text-left hover:shadow-md hover:border-blue-300 transition-all group"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1 min-w-0">
                    <h3 className="font-bold text-gray-900 text-lg mb-1 line-clamp-1 group-hover:text-blue-600 transition-colors">
                      {batch.name}
                    </h3>
                    <p className="text-sm text-gray-600 line-clamp-1">{batch.pipeline_name}</p>
                  </div>
                  <span className={`px-3 py-1 text-xs font-medium rounded-full border flex-shrink-0 ${getStatusColor(batch.status)}`}>
                    {batch.status}
                  </span>
                </div>

                <div className="space-y-3 mb-4">
                  <div className="flex items-center gap-2 text-sm">
                    <Calendar className="w-4 h-4 text-gray-400" />
                    <span className="text-gray-600">
                      {new Date(batch.start_date).toLocaleDateString()} - {new Date(batch.end_date).toLocaleDateString()}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <Users className="w-4 h-4 text-gray-400" />
                    <span className="text-gray-600">
                      {batch.current_enrollment} / {batch.max_capacity} students
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <TrendingUp className="w-4 h-4 text-gray-400" />
                    <span className="text-gray-600">{(batch.average_progress || 0).toFixed(0)}% average progress</span>
                  </div>
                </div>

                <div className="mb-4">
                  <div className="flex items-center justify-between text-xs text-gray-600 mb-2">
                    <span>Batch Progress</span>
                    <span className="font-medium">{(batch.average_progress || 0).toFixed(0)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                    <div
                      className="bg-gradient-to-r from-blue-500 to-purple-600 h-full transition-all"
                      style={{ width: `${batch.average_progress || 0}%` }}
                    />
                  </div>
                </div>

                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500">Click to view details</span>
                  <ArrowRight className="w-4 h-4 text-blue-600 group-hover:translate-x-1 transition-transform" />
                </div>
              </button>
            ))}
          </div>
        )}

        {!loading && filteredBatches.length > 0 && (
          <div className="mt-6 text-center text-sm text-gray-600">
            Showing {filteredBatches.length} of {batches.length} batches
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
