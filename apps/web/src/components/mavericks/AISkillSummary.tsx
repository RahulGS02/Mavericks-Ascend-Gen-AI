'use client';

import {
  Brain, Code2, Wrench, Database, Globe2, Users,
  Star, Briefcase, GraduationCap, FolderGit2, Award, Clock,
  ChevronDown, ChevronUp,
} from 'lucide-react';
import { useState } from 'react';

// ─── Types ────────────────────────────────────────────────────────────────────
interface Skills {
  technical?: string[];
  frameworks?: string[];
  tools?: string[];
  databases?: string[];
  languages?: string[];
  soft_skills?: string[];
}

interface Experience {
  company: string;
  role: string;            // backend field: role (not position)
  duration?: string;       // e.g. "Jan 2022 – Dec 2023"
  years?: number;          // numeric duration
  location?: string;
  description?: string;
  technologies?: string[];
}

interface Education {
  college: string;         // backend field: college (not institution)
  degree: string;
  branch?: string;         // backend field: branch (not field)
  university?: string;
  year?: number;           // graduation year
  cgpa?: number;           // backend field: cgpa (not gpa)
  percentage?: number;
}

interface Project {
  name: string;
  description?: string;
  technologies?: string[];
  role?: string;
  duration?: string;
  url?: string;
}

interface Certification {
  name: string;
  issuer?: string;
  year?: number;           // backend field: year (not date)
}

export interface ResumeData {
  summary?: string;
  skills?: Skills;
  experience?: Experience[];
  education?: Education[];
  projects?: Project[];
  certifications?: Certification[];
  total_experience_years?: number;
}

interface AISkillSummaryProps {
  summary?: string;
  resumeData?: ResumeData;
}

// ─── Skill category config ────────────────────────────────────────────────────
const SKILL_CATEGORIES = [
  {
    key: 'technical',
    label: 'Technical',
    icon: Code2,
    bg: 'bg-blue-100',
    text: 'text-blue-800',
    border: 'border-blue-200',
    dot: 'bg-blue-500',
  },
  {
    key: 'frameworks',
    label: 'Frameworks & Libraries',
    icon: Brain,
    bg: 'bg-purple-100',
    text: 'text-purple-800',
    border: 'border-purple-200',
    dot: 'bg-purple-500',
  },
  {
    key: 'tools',
    label: 'Tools & Platforms',
    icon: Wrench,
    bg: 'bg-orange-100',
    text: 'text-orange-800',
    border: 'border-orange-200',
    dot: 'bg-orange-500',
  },
  {
    key: 'databases',
    label: 'Databases',
    icon: Database,
    bg: 'bg-green-100',
    text: 'text-green-800',
    border: 'border-green-200',
    dot: 'bg-green-500',
  },
  {
    key: 'languages',
    label: 'Programming Languages',
    icon: Globe2,
    bg: 'bg-teal-100',
    text: 'text-teal-800',
    border: 'border-teal-200',
    dot: 'bg-teal-500',
  },
  {
    key: 'soft_skills',
    label: 'Soft Skills',
    icon: Users,
    bg: 'bg-pink-100',
    text: 'text-pink-800',
    border: 'border-pink-200',
    dot: 'bg-pink-500',
  },
];

// ─── Collapsible section wrapper ──────────────────────────────────────────────
function Section({
  title,
  icon: Icon,
  iconColor,
  count,
  children,
}: {
  title: string;
  icon: React.ElementType;
  iconColor: string;
  count?: number;
  children: React.ReactNode;
}) {
  const [open, setOpen] = useState(true);
  return (
    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center justify-between px-5 py-4 text-left hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center gap-2">
          <Icon className={`w-4 h-4 ${iconColor}`} />
          <span className="font-semibold text-gray-900 text-sm">{title}</span>
          {count !== undefined && (
            <span className="px-2 py-0.5 bg-gray-100 text-gray-500 rounded-full text-xs font-medium">
              {count}
            </span>
          )}
        </div>
        {open ? (
          <ChevronUp className="w-4 h-4 text-gray-400" />
        ) : (
          <ChevronDown className="w-4 h-4 text-gray-400" />
        )}
      </button>
      {open && <div className="px-5 pb-5">{children}</div>}
    </div>
  );
}

// ─── Main Component ───────────────────────────────────────────────────────────
export default function AISkillSummary({ summary, resumeData }: AISkillSummaryProps) {
  if (!summary && !resumeData) return null;

  const skills        = resumeData?.skills;
  const experience    = resumeData?.experience   ?? [];
  const education     = resumeData?.education    ?? [];
  const projects      = resumeData?.projects     ?? [];
  const certifications= resumeData?.certifications ?? [];
  const totalExp      = resumeData?.total_experience_years;
  const aiSummary     = resumeData?.summary ?? summary;

  // Count total detected skills
  const totalSkills = SKILL_CATEGORIES.reduce((acc, cat) => {
    return acc + (skills?.[cat.key as keyof Skills]?.length ?? 0);
  }, 0);

  return (
    <div className="space-y-4">

      {/* ── Header banner ──────────────────────────────────────────────── */}
      <div className="bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 rounded-xl p-5 text-white">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center shrink-0">
            <Brain className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="font-bold text-base">AI Skill Proficiency Summary</h3>
            <p className="text-blue-100 text-xs">Automatically extracted & analysed from your resume</p>
          </div>
        </div>

        {/* Quick stats */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mt-2">
          {totalSkills > 0 && (
            <div className="bg-white/10 rounded-lg px-3 py-2 text-center">
              <p className="text-2xl font-bold">{totalSkills}</p>
              <p className="text-blue-100 text-xs">Skills detected</p>
            </div>
          )}
          {experience.length > 0 && (
            <div className="bg-white/10 rounded-lg px-3 py-2 text-center">
              <p className="text-2xl font-bold">{experience.length}</p>
              <p className="text-blue-100 text-xs">Experience{experience.length > 1 ? 's' : ''}</p>
            </div>
          )}
          {projects.length > 0 && (
            <div className="bg-white/10 rounded-lg px-3 py-2 text-center">
              <p className="text-2xl font-bold">{projects.length}</p>
              <p className="text-blue-100 text-xs">Project{projects.length > 1 ? 's' : ''}</p>
            </div>
          )}
          {totalExp !== undefined && totalExp !== null && (
            <div className="bg-white/10 rounded-lg px-3 py-2 text-center">
              <p className="text-2xl font-bold">{totalExp}</p>
              <p className="text-blue-100 text-xs">Yrs experience</p>
            </div>
          )}
        </div>
      </div>

      {/* ── Professional Summary ────────────────────────────────────────── */}
      {aiSummary && (
        <Section title="Professional Summary" icon={Star} iconColor="text-yellow-500">
          <p className="text-gray-700 text-sm leading-relaxed">{aiSummary}</p>
        </Section>
      )}

      {/* ── Skills by Category ──────────────────────────────────────────── */}
      {skills && totalSkills > 0 && (
        <Section
          title="Skills by Category"
          icon={Code2}
          iconColor="text-blue-500"
          count={totalSkills}
        >
          <div className="space-y-4">
            {SKILL_CATEGORIES.map(({ key, label, icon: Icon, bg, text, border, dot }) => {
              const catSkills = skills[key as keyof Skills] ?? [];
              if (catSkills.length === 0) return null;
              return (
                <div key={key}>
                  <div className="flex items-center gap-2 mb-2">
                    <span className={`w-2 h-2 rounded-full ${dot}`} />
                    <Icon className="w-3.5 h-3.5 text-gray-500" />
                    <span className="text-xs font-semibold text-gray-600 uppercase tracking-wide">
                      {label}
                    </span>
                    <span className="text-xs text-gray-400">({catSkills.length})</span>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {catSkills.map((skill, i) => (
                      <span
                        key={i}
                        className={`px-2.5 py-1 rounded-full text-xs font-medium border ${bg} ${text} ${border}`}
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </Section>
      )}

      {/* ── Work Experience ─────────────────────────────────────────────── */}
      {experience.length > 0 && (
        <Section
          title="Work Experience"
          icon={Briefcase}
          iconColor="text-indigo-500"
          count={experience.length}
        >
          <div className="space-y-4">
            {experience.map((exp, i) => (
              <div key={i} className="relative pl-5 border-l-2 border-indigo-100">
                <div className="absolute -left-[9px] top-1 w-4 h-4 rounded-full bg-indigo-500 border-2 border-white" />
                <p className="font-semibold text-gray-900 text-sm">{exp.role}</p>
                <p className="text-indigo-600 text-sm font-medium">{exp.company}</p>
                {(exp.duration || exp.years) && (
                  <div className="flex items-center gap-1 text-gray-400 text-xs mt-0.5">
                    <Clock className="w-3 h-3" />
                    <span>
                      {exp.duration
                        ? exp.duration
                        : `${exp.years} yr${exp.years !== 1 ? 's' : ''}`}
                    </span>
                  </div>
                )}
                {exp.location && (
                  <p className="text-gray-400 text-xs">{exp.location}</p>
                )}
                {exp.description && (
                  <p className="text-gray-600 text-xs mt-1.5 leading-relaxed line-clamp-3">
                    {exp.description}
                  </p>
                )}
                {exp.technologies && exp.technologies.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {exp.technologies.map((tech, j) => (
                      <span
                        key={j}
                        className="px-2 py-0.5 bg-indigo-50 text-indigo-700 border border-indigo-100 rounded text-xs"
                      >
                        {tech}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </Section>
      )}

      {/* ── Education ───────────────────────────────────────────────────── */}
      {education.length > 0 && (
        <Section
          title="Education"
          icon={GraduationCap}
          iconColor="text-green-500"
          count={education.length}
        >
          <div className="space-y-3">
            {education.map((edu, i) => (
              <div key={i} className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center shrink-0 mt-0.5">
                  <GraduationCap className="w-4 h-4 text-green-600" />
                </div>
                <div>
                  <p className="font-semibold text-gray-900 text-sm">
                    {edu.degree}{edu.branch ? ` in ${edu.branch}` : ''}
                  </p>
                  <p className="text-gray-600 text-sm">{edu.college}</p>
                  {edu.university && edu.university !== edu.college && (
                    <p className="text-gray-500 text-xs">{edu.university}</p>
                  )}
                  {edu.year && (
                    <p className="text-gray-400 text-xs mt-0.5">Graduated {edu.year}</p>
                  )}
                  {edu.cgpa !== undefined && edu.cgpa !== null && (
                    <span className="inline-block mt-1 px-2 py-0.5 bg-green-50 text-green-700 rounded text-xs font-medium">
                      CGPA: {edu.cgpa}
                    </span>
                  )}
                  {edu.percentage !== undefined && edu.percentage !== null && (
                    <span className="inline-block mt-1 ml-1 px-2 py-0.5 bg-green-50 text-green-700 rounded text-xs font-medium">
                      {edu.percentage}%
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </Section>
      )}

      {/* ── Projects ────────────────────────────────────────────────────── */}
      {projects.length > 0 && (
        <Section
          title="Projects"
          icon={FolderGit2}
          iconColor="text-purple-500"
          count={projects.length}
        >
          <div className="space-y-3">
            {projects.map((proj, i) => (
              <div
                key={i}
                className="p-3 bg-purple-50 rounded-lg border border-purple-100"
              >
                <div className="flex items-start justify-between gap-2">
                  <p className="font-semibold text-gray-900 text-sm">{proj.name}</p>
                  {proj.url && (
                    <a
                      href={proj.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-purple-600 hover:text-purple-800 hover:underline shrink-0"
                    >
                      View →
                    </a>
                  )}
                </div>
                {proj.description && (
                  <p className="text-gray-600 text-xs mt-1 leading-relaxed line-clamp-2">
                    {proj.description}
                  </p>
                )}
                {proj.technologies && proj.technologies.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {proj.technologies.map((tech, j) => (
                      <span
                        key={j}
                        className="px-2 py-0.5 bg-white border border-purple-200 text-purple-700 rounded text-xs font-medium"
                      >
                        {tech}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </Section>
      )}

      {/* ── Certifications ──────────────────────────────────────────────── */}
      {certifications.length > 0 && (
        <Section
          title="Certifications"
          icon={Award}
          iconColor="text-yellow-500"
          count={certifications.length}
        >
          <div className="space-y-2">
            {certifications.map((cert, i) => (
              <div key={i} className="flex items-start gap-3">
                <div className="w-7 h-7 rounded-full bg-yellow-100 flex items-center justify-center shrink-0 mt-0.5">
                  <Award className="w-3.5 h-3.5 text-yellow-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900 text-sm">{cert.name}</p>
                  {cert.issuer && (
                    <p className="text-gray-500 text-xs">{cert.issuer}</p>
                  )}
                  {cert.year && (
                    <p className="text-gray-400 text-xs">{cert.year}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </Section>
      )}
    </div>
  );
}
