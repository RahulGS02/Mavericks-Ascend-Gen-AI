"use client";

import { useState, useCallback, useRef } from 'react';
import { Plus, Save, Copy, Trash2, CheckCircle, Clock } from 'lucide-react';
import { toast } from 'sonner';

interface Job {
  id: string;
  name: string;
  description: string;
  job_type: 'TRAINING' | 'ASSESSMENT' | 'CERTIFICATION' | 'UDEMY_COURSE' | 'EXTERNAL_CERTIFICATION' | 'DEPLOYMENT' | 'CUSTOM';
  sequence_order: number;
  duration_days: number;
  x: number;
  y: number;
  status?: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED';
}

interface Connection {
  from: string;
  to: string;
}

interface PipelineVisualEditorProps {
  initialJobs?: Job[];
  initialConnections?: Connection[];
  onSave: (jobs: Job[], connections: Connection[]) => void;
  pipelineName?: string;
  readOnly?: boolean;
}

export default function PipelineVisualEditor({
  initialJobs = [],
  initialConnections = [],
  onSave,
  pipelineName = "Untitled Pipeline",
  readOnly = false
}: PipelineVisualEditorProps) {
  const [jobs, setJobs] = useState<Job[]>(initialJobs);
  const [connections, setConnections] = useState<Connection[]>(initialConnections);
  const [selectedJob, setSelectedJob] = useState<string | null>(null);
  const [draggedJob, setDraggedJob] = useState<string | null>(null);
  const [connectingFrom, setConnectingFrom] = useState<string | null>(null);
  const [hoveredJob, setHoveredJob] = useState<string | null>(null);
  const [showAddMenu, setShowAddMenu] = useState(false);
  const [isDraggingConnection, setIsDraggingConnection] = useState(false);
  const [tempConnectionEnd, setTempConnectionEnd] = useState<{ x: number; y: number } | null>(null);
  const canvasRef = useRef<HTMLDivElement>(null);

  const jobTypeColors = {
    TRAINING: { bg: 'bg-blue-50', border: 'border-blue-300', text: 'text-blue-700', icon: '🎓', label: 'Training' },
    ASSESSMENT: { bg: 'bg-purple-50', border: 'border-purple-300', text: 'text-purple-700', icon: '📝', label: 'Assessment' },
    CERTIFICATION: { bg: 'bg-yellow-50', border: 'border-yellow-300', text: 'text-yellow-700', icon: '🏆', label: 'Certification' },
    UDEMY_COURSE: { bg: 'bg-orange-50', border: 'border-orange-300', text: 'text-orange-700', icon: '📚', label: 'Udemy Course' },
    EXTERNAL_CERTIFICATION: { bg: 'bg-indigo-50', border: 'border-indigo-300', text: 'text-indigo-700', icon: '🎖️', label: 'External Cert' },
    DEPLOYMENT: { bg: 'bg-green-50', border: 'border-green-300', text: 'text-green-700', icon: '🚀', label: 'Deployment' },
    CUSTOM: { bg: 'bg-gray-50', border: 'border-gray-300', text: 'text-gray-700', icon: '⚙️', label: 'Custom Job' }
  };

  const addJob = (type: Job['job_type']) => {
    const durationMap = {
      TRAINING: 14,
      ASSESSMENT: 2,
      CERTIFICATION: 7,
      UDEMY_COURSE: 21,
      EXTERNAL_CERTIFICATION: 30,
      DEPLOYMENT: 90,
      CUSTOM: 7
    };

    const nameMap = {
      TRAINING: 'New Training',
      ASSESSMENT: 'New Assessment',
      CERTIFICATION: 'New Certification',
      UDEMY_COURSE: 'Udemy Course',
      EXTERNAL_CERTIFICATION: 'External Certification',
      DEPLOYMENT: 'New Deployment',
      CUSTOM: 'Custom Job'
    };

    const newJob: Job = {
      id: `job-${Date.now()}`,
      name: nameMap[type],
      description: '',
      job_type: type,
      sequence_order: jobs.length + 1,
      duration_days: durationMap[type],
      x: 100 + (jobs.length * 50),
      y: 100 + (jobs.length % 3) * 150,
      status: 'PENDING'
    };
    setJobs([...jobs, newJob]);
    setShowAddMenu(false);
  };

  const updateJob = (id: string, updates: Partial<Job>) => {
    setJobs(jobs.map(j => j.id === id ? { ...j, ...updates } : j));
  };

  const deleteJob = (id: string) => {
    setJobs(jobs.filter(j => j.id !== id));
    setConnections(connections.filter(c => c.from !== id && c.to !== id));
    setSelectedJob(null);
  };

  const handleDragStart = (e: React.DragEvent, jobId: string) => {
    if (readOnly) return;
    setDraggedJob(jobId);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDrag = (e: React.DragEvent, jobId: string) => {
    if (readOnly || !canvasRef.current) return;
    const rect = canvasRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left - 100;
    const y = e.clientY - rect.top - 40;
    if (x > 0 && y > 0) {
      updateJob(jobId, { x, y });
    }
  };

  const handleDragEnd = () => {
    setDraggedJob(null);
  };

  const startConnectionDrag = (jobId: string, e: React.MouseEvent) => {
    if (readOnly) return;
    e.stopPropagation();
    e.preventDefault();

    setConnectingFrom(jobId);
    setIsDraggingConnection(true);

    // Get initial mouse position
    if (canvasRef.current) {
      const rect = canvasRef.current.getBoundingClientRect();
      setTempConnectionEnd({
        x: e.clientX - rect.left,
        y: e.clientY - rect.top
      });
    }
  };

  const handleConnectionDrag = (e: React.MouseEvent) => {
    if (!isDraggingConnection || !canvasRef.current) return;

    const rect = canvasRef.current.getBoundingClientRect();
    setTempConnectionEnd({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    });
  };

  const endConnectionDrag = (targetJobId?: string) => {
    if (!isDraggingConnection || !connectingFrom) {
      setIsDraggingConnection(false);
      setConnectingFrom(null);
      setTempConnectionEnd(null);
      return;
    }

    if (targetJobId && targetJobId !== connectingFrom) {
      // Check if connection already exists
      if (connections.find(c => c.from === connectingFrom && c.to === targetJobId)) {
        toast.error('Connection already exists');
      } else {
        setConnections([...connections, { from: connectingFrom, to: targetJobId }]);
        toast.success('Jobs connected!');
      }
    }

    setIsDraggingConnection(false);
    setConnectingFrom(null);
    setTempConnectionEnd(null);
  };

  const deleteConnection = (from: string, to: string) => {
    setConnections(connections.filter(c => !(c.from === from && c.to === to)));
  };

  const handleSave = () => {
    onSave(jobs, connections);
  };

  const getJobPosition = (jobId: string) => {
    const job = jobs.find(j => j.id === jobId);
    if (!job) return { x: 0, y: 0 };

    // Job cards are 200px wide and positioned at job.x, job.y
    // Return center point of the card for connections
    const cardWidth = 200;
    const cardHeight = 120; // Approximate card height

    return {
      x: job.x + cardWidth / 2,  // Center horizontally
      y: job.y + cardHeight / 2  // Center vertically
    };
  };

  return (
    <div className="w-full h-full flex flex-col bg-gray-50">
      {/* Toolbar */}
      <div className="bg-white border-b border-gray-200 p-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h2 className="text-xl font-semibold text-gray-900">{pipelineName}</h2>
          <span className="text-sm text-gray-500">{jobs.length} jobs</span>
          {isDraggingConnection && (
            <div className="flex items-center gap-2 bg-blue-100 border border-blue-300 px-4 py-2 rounded-md animate-pulse">
              <span className="text-blue-700 font-medium">🔗 Drag to another job's input point (left circle)</span>
            </div>
          )}
        </div>
        
        {!readOnly && (
          <div className="flex gap-2">
            <div className="relative">
              <button
                onClick={() => setShowAddMenu(!showAddMenu)}
                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                <Plus className="w-4 h-4 mr-2" />
                Add Job
              </button>
              
              {showAddMenu && (
                <div className="absolute top-full mt-2 right-0 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-10 min-w-[240px] max-h-96 overflow-y-auto">
                  <button
                    onClick={() => addJob('TRAINING')}
                    className="w-full px-4 py-2 text-left hover:bg-blue-50 flex items-center gap-3"
                  >
                    <span className="text-2xl">🎓</span>
                    <div>
                      <div className="font-medium">Training</div>
                      <div className="text-xs text-gray-500">Learning activities</div>
                    </div>
                  </button>
                  <button
                    onClick={() => addJob('ASSESSMENT')}
                    className="w-full px-4 py-2 text-left hover:bg-purple-50 flex items-center gap-3"
                  >
                    <span className="text-2xl">📝</span>
                    <div>
                      <div className="font-medium">Assessment</div>
                      <div className="text-xs text-gray-500">Tests & evaluations</div>
                    </div>
                  </button>
                  <button
                    onClick={() => addJob('CERTIFICATION')}
                    className="w-full px-4 py-2 text-left hover:bg-yellow-50 flex items-center gap-3"
                  >
                    <span className="text-2xl">🏆</span>
                    <div>
                      <div className="font-medium">Certification</div>
                      <div className="text-xs text-gray-500">Internal certification</div>
                    </div>
                  </button>
                  <button
                    onClick={() => addJob('UDEMY_COURSE')}
                    className="w-full px-4 py-2 text-left hover:bg-orange-50 flex items-center gap-3"
                  >
                    <span className="text-2xl">📚</span>
                    <div>
                      <div className="font-medium">Udemy Course</div>
                      <div className="text-xs text-gray-500">Online course completion</div>
                    </div>
                  </button>
                  <button
                    onClick={() => addJob('EXTERNAL_CERTIFICATION')}
                    className="w-full px-4 py-2 text-left hover:bg-indigo-50 flex items-center gap-3"
                  >
                    <span className="text-2xl">🎖️</span>
                    <div>
                      <div className="font-medium">External Certification</div>
                      <div className="text-xs text-gray-500">AWS, Azure, etc.</div>
                    </div>
                  </button>
                  <button
                    onClick={() => addJob('DEPLOYMENT')}
                    className="w-full px-4 py-2 text-left hover:bg-green-50 flex items-center gap-3"
                  >
                    <span className="text-2xl">🚀</span>
                    <div>
                      <div className="font-medium">Deployment</div>
                      <div className="text-xs text-gray-500">Client project work</div>
                    </div>
                  </button>
                  <button
                    onClick={() => addJob('CUSTOM')}
                    className="w-full px-4 py-2 text-left hover:bg-gray-50 flex items-center gap-3"
                  >
                    <span className="text-2xl">⚙️</span>
                    <div>
                      <div className="font-medium">Custom Job</div>
                      <div className="text-xs text-gray-500">Define your own</div>
                    </div>
                  </button>
                </div>
              )}
            </div>

            <button
              onClick={handleSave}
              className="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
            >
              <Save className="w-4 h-4 mr-2" />
              Save Pipeline
            </button>
          </div>
        )}
      </div>

      {/* Canvas */}
      <div
        ref={canvasRef}
        className="flex-1 relative overflow-auto bg-gradient-to-br from-gray-50 to-gray-100"
        style={{
          backgroundImage: 'radial-gradient(circle, #e5e7eb 1px, transparent 1px)',
          backgroundSize: '20px 20px'
        }}
        onMouseMove={handleConnectionDrag}
        onMouseUp={() => endConnectionDrag()}
      >
        <svg className="absolute inset-0 w-full h-full" style={{ zIndex: 1, pointerEvents: 'none' }}>
          {/* Existing connections */}
          {connections.map((conn, idx) => {
            const fromCenter = getJobPosition(conn.from);
            const toCenter = getJobPosition(conn.to);

            // Connection points: from right side of source, to left side of target
            const cardWidth = 200;
            const fromX = fromCenter.x + cardWidth / 2;  // Right edge
            const fromY = fromCenter.y;
            const toX = toCenter.x - cardWidth / 2;      // Left edge
            const toY = toCenter.y;

            // Create curved path
            const midX = (fromX + toX) / 2;
            const path = `M ${fromX} ${fromY}
                         C ${midX} ${fromY}, ${midX} ${toY}, ${toX} ${toY}`;

            return (
              <g key={idx}>
                <path
                  d={path}
                  stroke="#9ca3af"
                  strokeWidth="2"
                  fill="none"
                  markerEnd="url(#arrowhead)"
                />
                {!readOnly && (
                  <circle
                    cx={(fromX + toX) / 2}
                    cy={(fromY + toY) / 2}
                    r="12"
                    fill="white"
                    stroke="#ef4444"
                    strokeWidth="3"
                    style={{ cursor: 'pointer', pointerEvents: 'auto' }}
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteConnection(conn.from, conn.to);
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.setAttribute('r', '14');
                      e.currentTarget.setAttribute('fill', '#fee2e2');
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.setAttribute('r', '12');
                      e.currentTarget.setAttribute('fill', 'white');
                    }}
                  >
                    <title>Click to delete connection</title>
                  </circle>
                )}
              </g>
            );
          })}

          {/* Temporary connection while dragging */}
          {isDraggingConnection && connectingFrom && tempConnectionEnd && (
            <g>
              <path
                d={`M ${getJobPosition(connectingFrom).x + 100} ${getJobPosition(connectingFrom).y}
                   L ${tempConnectionEnd.x} ${tempConnectionEnd.y}`}
                stroke="#3b82f6"
                strokeWidth="3"
                strokeDasharray="5,5"
                fill="none"
                className="animate-pulse"
              />
              <circle
                cx={tempConnectionEnd.x}
                cy={tempConnectionEnd.y}
                r="6"
                fill="#3b82f6"
              />
            </g>
          )}

          <defs>
            <marker
              id="arrowhead"
              markerWidth="10"
              markerHeight="10"
              refX="9"
              refY="3"
              orient="auto"
            >
              <polygon points="0 0, 10 3, 0 6" fill="#9ca3af" />
            </marker>
          </defs>
        </svg>

        {/* Jobs */}
        <div className="relative" style={{ minHeight: '600px', minWidth: '1000px', zIndex: 2 }}>
          {jobs.map((job) => {
            const colors = jobTypeColors[job.job_type];
            const isSelected = selectedJob === job.id;
            const isConnecting = connectingFrom === job.id;

            return (
              <div
                key={job.id}
                draggable={!readOnly}
                onDragStart={(e) => handleDragStart(e, job.id)}
                onDrag={(e) => handleDrag(e, job.id)}
                onDragEnd={handleDragEnd}
                onClick={(e) => {
                  if (connectingFrom && connectingFrom !== job.id) {
                    startConnection(job.id, e);
                  } else {
                    setSelectedJob(job.id);
                  }
                }}
                onMouseEnter={() => setHoveredJob(job.id)}
                onMouseLeave={() => setHoveredJob(null)}
                className={`absolute cursor-move transition-all ${
                  isSelected ? 'ring-4 ring-blue-500 scale-105' : ''
                } ${isConnecting ? 'ring-4 ring-yellow-400 animate-pulse scale-110' : ''}
                   ${connectingFrom && hoveredJob === job.id && connectingFrom !== job.id ? 'ring-4 ring-green-400 scale-105' : ''}`}
                style={{
                  left: `${job.x}px`,
                  top: `${job.y}px`,
                  width: '200px'
                }}
              >
                <div className={`bg-white rounded-lg border-2 ${colors.border} shadow-lg hover:shadow-xl transition-shadow`}>
                  {/* Status indicator */}
                  <div className={`h-2 ${colors.bg} rounded-t-lg`}></div>

                  {/* Header */}
                  <div className={`p-3 ${colors.bg} border-b ${colors.border}`}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-2xl">{colors.icon}</span>
                      <span className="text-xs font-semibold text-gray-600">#{job.sequence_order}</span>
                    </div>
                    {!readOnly ? (
                      <input
                        type="text"
                        value={job.name}
                        onChange={(e) => updateJob(job.id, { name: e.target.value })}
                        className={`w-full font-semibold ${colors.text} bg-transparent border-none focus:outline-none text-sm`}
                        onClick={(e) => e.stopPropagation()}
                      />
                    ) : (
                      <p className={`font-semibold ${colors.text} text-sm`}>{job.name}</p>
                    )}
                  </div>

                  {/* Body */}
                  <div className="p-3 space-y-2">
                    <div className="flex items-center justify-between text-xs text-gray-600">
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {job.duration_days}d
                      </span>
                      <span className="px-2 py-0.5 bg-gray-100 rounded text-xs">
                        {job.job_type}
                      </span>
                    </div>

                    {job.status === 'COMPLETED' && (
                      <div className="flex items-center gap-1 text-xs text-green-600">
                        <CheckCircle className="w-3 h-3" />
                        <span>Completed</span>
                      </div>
                    )}
                  </div>

                  {/* Actions */}
                  {!readOnly && (
                    <div className="p-2 border-t border-gray-200 flex gap-2">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteJob(job.id);
                        }}
                        className="flex-1 px-3 py-2 text-xs bg-red-50 text-red-600 rounded hover:bg-red-100"
                        title="Delete job"
                      >
                        <Trash2 className="w-3 h-3 mr-1 inline" />
                        Delete
                      </button>
                    </div>
                  )}
                </div>

                {/* Connection points - Draggable */}
                {!readOnly && (
                  <>
                    {/* Output connection point (right side) */}
                    <div
                      className={`absolute -right-3 top-1/2 -mt-3 w-6 h-6 rounded-full border-3 border-white shadow-lg cursor-pointer transition-all hover:scale-125 ${
                        isDraggingConnection && connectingFrom === job.id
                          ? 'bg-blue-500 animate-pulse scale-125'
                          : 'bg-blue-500 hover:bg-blue-600'
                      }`}
                      onMouseDown={(e) => startConnectionDrag(job.id, e)}
                      title="Drag to connect"
                      style={{ zIndex: 10 }}
                    >
                      <div className="absolute inset-0 flex items-center justify-center text-white text-xs font-bold">→</div>
                    </div>

                    {/* Input connection point (left side) */}
                    <div
                      className={`absolute -left-3 top-1/2 -mt-3 w-6 h-6 rounded-full border-3 border-white shadow-lg transition-all ${
                        isDraggingConnection && connectingFrom !== job.id
                          ? 'bg-green-500 scale-125 cursor-pointer'
                          : 'bg-gray-400'
                      }`}
                      onMouseUp={() => endConnectionDrag(job.id)}
                      onMouseEnter={() => isDraggingConnection && setHoveredJob(job.id)}
                      onMouseLeave={() => setHoveredJob(null)}
                      title="Drop here to connect"
                      style={{ zIndex: 10 }}
                    >
                      <div className="absolute inset-0 flex items-center justify-center text-white text-xs font-bold">←</div>
                    </div>
                  </>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Instructions */}
      {!readOnly && jobs.length === 0 && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="text-center text-gray-400">
            <p className="text-lg font-medium">Click "Add Job" to start building your pipeline</p>
            <p className="text-sm mt-2">💡 Drag jobs to position them</p>
            <p className="text-sm mt-1">🔗 Drag from blue circle (→) to another job's gray circle (←) to connect</p>
          </div>
        </div>
      )}
    </div>
  );
}
