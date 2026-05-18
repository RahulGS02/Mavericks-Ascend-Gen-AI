interface ProfileStatusBadgeProps {
  status: 'DRAFT' | 'SUBMITTED' | 'UNDER_REVIEW' | 'APPROVED' | 'REJECTED';
}

const statusConfig = {
  DRAFT: {
    label: 'Draft',
    color: 'bg-gray-100 text-gray-800 border-gray-300',
    icon: '📝'
  },
  SUBMITTED: {
    label: 'Submitted',
    color: 'bg-blue-100 text-blue-800 border-blue-300',
    icon: '📤'
  },
  UNDER_REVIEW: {
    label: 'Under Review',
    color: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    icon: '🔍'
  },
  APPROVED: {
    label: 'Approved',
    color: 'bg-green-100 text-green-800 border-green-300',
    icon: '✅'
  },
  REJECTED: {
    label: 'Rejected',
    color: 'bg-red-100 text-red-800 border-red-300',
    icon: '❌'
  }
};

export default function ProfileStatusBadge({ status }: ProfileStatusBadgeProps) {
  const config = statusConfig[status];

  return (
    <span className={`inline-flex items-center gap-1 px-3 py-1 border rounded-full text-sm font-medium ${config.color}`}>
      <span>{config.icon}</span>
      <span>{config.label}</span>
    </span>
  );
}
