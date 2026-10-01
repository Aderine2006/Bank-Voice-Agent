'use client';

interface DashboardProps {
  conversationState: any;
}

export default function Dashboard({ conversationState }: DashboardProps) {
  const stages = [
    'greeting',
    'intent_detection',
    'loan_discovery',
    'profile_collection',
    'product_matching',
    'eligibility_check',
  ];

  const currentStageIndex = stages.indexOf(conversationState?.current_stage || 'greeting');

  return (
    <div className="glass-card p-6">
      <h3 className="text-lg font-semibold mb-4 gradient-text">Conversation Dashboard</h3>
      
      {/* Workflow Progress */}
      <div className="mb-6">
        <p className="text-xs text-gray-500 mb-2">Workflow Stage</p>
        <div className="flex items-center gap-2">
          {stages.map((stage, index) => (
            <React.Fragment key={stage}>
              <div
                className={`h-2 flex-1 rounded-full transition-colors ${
                  index <= currentStageIndex ? 'bg-primary-500' : 'bg-gray-700'
                }`}
              />
              {index < stages.length - 1 && (
                <div className="w-1 h-1 rounded-full bg-gray-600" />
              )}
            </React.Fragment>
          ))}
        </div>
        <p className="text-xs text-gray-400 mt-2 capitalize">
          {conversationState?.current_stage?.replace('_', ' ')}
        </p>
      </div>

      {/* Intent */}
      <div className="mb-4">
        <p className="text-xs text-gray-500 mb-1">Detected Intent</p>
        <p className="text-sm text-gray-100 capitalize">
          {conversationState?.intent?.replace('_', ' ') || 'Unknown'}
        </p>
      </div>

      {/* Missing Information */}
      {conversationState?.missing_fields && conversationState.missing_fields.length > 0 && (
        <div className="mb-4">
          <p className="text-xs text-gray-500 mb-2">Missing Information</p>
          <div className="flex flex-wrap gap-2">
            {conversationState.missing_fields.map((field: string, index: number) => (
              <span
                key={index}
                className="px-2 py-1 bg-yellow-500/20 text-yellow-400 text-xs rounded-md"
              >
                {field.replace('_', ' ')}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Statistics */}
      <div className="grid grid-cols-3 gap-4 mt-6">
        <div className="text-center p-3 bg-gray-800/50 rounded-xl">
          <p className="text-2xl font-semibold text-primary-500">
            {conversationState?.candidate_products?.length || 0}
          </p>
          <p className="text-xs text-gray-500">Candidates</p>
        </div>
        <div className="text-center p-3 bg-gray-800/50 rounded-xl">
          <p className="text-2xl font-semibold text-green-500">
            {conversationState?.eligible_products?.length || 0}
          </p>
          <p className="text-xs text-gray-500">Eligible</p>
        </div>
        <div className="text-center p-3 bg-gray-800/50 rounded-xl">
          <p className="text-2xl font-semibold text-red-500">
            {conversationState?.ineligible_products?.length || 0}
          </p>
          <p className="text-xs text-gray-500">Ineligible</p>
        </div>
      </div>
    </div>
  );
}

import React from 'react';
