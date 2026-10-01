'use client';

import { CheckCircle, XCircle, Clock, IndianRupee } from 'lucide-react';

interface LoanMatchesProps {
  matches: any[];
}

export default function LoanMatches({ matches }: LoanMatchesProps) {
  if (!matches || matches.length === 0) {
    return (
      <div className="glass-card p-6">
        <h3 className="text-lg font-semibold mb-4 gradient-text">Loan Matches</h3>
        <p className="text-sm text-gray-500 text-center py-4">
          No matching products yet
        </p>
      </div>
    );
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'ELIGIBLE_BASED_ON_PROVIDED_INFORMATION':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'MORE_INFORMATION_REQUIRED':
        return <Clock className="w-5 h-5 text-yellow-500" />;
      case 'DOES_NOT_MEET_CONFIGURED_CRITERIA':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <Clock className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'ELIGIBLE_BASED_ON_PROVIDED_INFORMATION':
        return 'Eligible';
      case 'MORE_INFORMATION_REQUIRED':
        return 'More info needed';
      case 'DOES_NOT_MEET_CONFIGURED_CRITERIA':
        return 'Not eligible';
      default:
        return 'Unknown';
    }
  };

  return (
    <div className="glass-card p-6">
      <h3 className="text-lg font-semibold mb-4 gradient-text">Loan Matches</h3>
      
      <div className="space-y-4">
        {matches.map((match, index) => (
          <div
            key={index}
            className="p-4 bg-gray-800/50 rounded-xl border border-gray-700 hover:border-gray-600 transition-colors"
          >
            <div className="flex items-start justify-between mb-3">
              <div>
                <h4 className="font-medium text-gray-100">{match.product_name}</h4>
                <p className="text-xs text-gray-500 mt-1">{match.product_id}</p>
              </div>
              <div className="flex items-center gap-2">
                {getStatusIcon(match.status)}
                <span className="text-xs text-gray-400">{getStatusText(match.status)}</span>
              </div>
            </div>

            {match.match_score && (
              <div className="mb-3">
                <div className="flex items-center justify-between text-xs text-gray-400 mb-1">
                  <span>Match Score</span>
                  <span>{match.match_score}%</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-primary-500 h-2 rounded-full transition-all"
                    style={{ width: `${match.match_score}%` }}
                  />
                </div>
              </div>
            )}

            {match.emi && (
              <div className="flex items-center gap-2 text-sm text-gray-300">
                <IndianRupee className="w-4 h-4" />
                <span>Est. EMI: ₹{match.emi.toLocaleString('en-IN')}/month</span>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
