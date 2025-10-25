import React from 'react';

interface DataQualityReportData {
    overallScore: number;
    missingDataSources: string[];
    recommendations: string[];
}

interface DataQualityReportProps {
    report: DataQualityReportData;
}

const DataQualityReport: React.FC<DataQualityReportProps> = ({ report }) => {
    const getScoreColor = (score: number): string => {
        if (score >= 0.8) return 'text-green-600 bg-green-100';
        if (score >= 0.6) return 'text-yellow-600 bg-yellow-100';
        return 'text-red-600 bg-red-100';
    };

    const getScoreLabel = (score: number): string => {
        if (score >= 0.8) return 'Excellent';
        if (score >= 0.6) return 'Good';
        return 'Limited';
    };

    const getScoreDescription = (score: number): string => {
        if (score >= 0.8) return 'High-quality data available for most products with multiple sources and recent updates.';
        if (score >= 0.6) return 'Moderate data quality with some limitations in coverage or freshness.';
        return 'Limited data availability. Results may be less accurate due to missing information.';
    };

    return (
        <div className="glass-card p-8 group hover:scale-[1.02] transition-all duration-300">
            <div className="flex items-center space-x-4 mb-8">
                <div className="w-14 h-14 bg-gradient-accent rounded-2xl flex items-center justify-center">
                    <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                    </svg>
                </div>
                <div>
                    <h2 className="text-3xl font-bold text-white">Data Quality Report</h2>
                    <p className="text-gray-300">Transparency and confidence in our analysis</p>
                </div>
            </div>

            {/* Overall Score */}
            <div className="mb-8">
                <div className="flex items-center justify-between mb-6">
                    <h3 className="text-xl font-semibold text-white">Overall Data Quality</h3>
                    <span className={`inline-flex items-center px-4 py-2 rounded-xl text-sm font-bold border ${report.overallScore >= 0.8 ? 'bg-green-500/20 text-green-300 border-green-500/30' :
                        report.overallScore >= 0.6 ? 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30' :
                            'bg-red-500/20 text-red-300 border-red-500/30'
                        }`}>
                        {getScoreLabel(report.overallScore)} ({Math.round(report.overallScore * 100)}%)
                    </span>
                </div>

                <div className="glass-card p-6 border-white/10 mb-4">
                    <div className="w-full bg-white/20 rounded-full h-4 mb-4 overflow-hidden">
                        <div
                            className={`h-4 rounded-full transition-all duration-1000 ${report.overallScore >= 0.8 ? 'bg-gradient-to-r from-green-400 to-green-500' :
                                report.overallScore >= 0.6 ? 'bg-gradient-to-r from-yellow-400 to-yellow-500' :
                                    'bg-gradient-to-r from-red-400 to-red-500'
                                }`}
                            style={{ width: `${report.overallScore * 100}%` }}
                        ></div>
                    </div>
                    <p className="text-gray-300 leading-relaxed">
                        {getScoreDescription(report.overallScore)}
                    </p>
                </div>
            </div>

            {/* Missing Data Sources */}
            {report.missingDataSources && report.missingDataSources.length > 0 && (
                <div className="mb-8">
                    <h3 className="text-xl font-semibold text-white mb-6 flex items-center space-x-3">
                        <svg className="w-6 h-6 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                        </svg>
                        <span>Missing Data Sources</span>
                    </h3>
                    <div className="glass-card p-6 border-yellow-400/30 bg-yellow-500/10">
                        <div className="flex items-start space-x-4">
                            <div className="w-12 h-12 bg-gradient-to-r from-yellow-500 to-yellow-600 rounded-xl flex items-center justify-center flex-shrink-0">
                                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                                </svg>
                            </div>
                            <div>
                                <h4 className="text-lg font-semibold text-yellow-300 mb-3">
                                    Some data sources are currently unavailable
                                </h4>
                                <div className="space-y-2">
                                    {report.missingDataSources.map((source, index) => (
                                        <div key={index} className="flex items-center space-x-3">
                                            <div className="w-2 h-2 bg-yellow-400 rounded-full"></div>
                                            <span className="text-gray-300">{source}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Recommendations */}
            {report.recommendations && report.recommendations.length > 0 && (
                <div className="mb-8">
                    <h3 className="text-xl font-semibold text-white mb-6 flex items-center space-x-3">
                        <svg className="w-6 h-6 text-accent-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                        </svg>
                        <span>Data Quality Recommendations</span>
                    </h3>
                    <div className="space-y-4">
                        {report.recommendations.map((recommendation, index) => (
                            <div key={index} className="glass-card p-4 border-accent-400/20 bg-accent-500/10">
                                <div className="flex items-start space-x-3">
                                    <div className="w-8 h-8 bg-gradient-accent rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                                        <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                                            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                                        </svg>
                                    </div>
                                    <p className="text-gray-300 leading-relaxed">{recommendation}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Data Quality Legend */}
            <div className="pt-8 border-t border-white/20">
                <h4 className="text-lg font-semibold text-white mb-6">Data Quality Factors</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="glass-card p-4 border-white/10">
                        <div className="flex items-center space-x-3 mb-2">
                            <div className="w-3 h-3 bg-gradient-to-r from-green-400 to-green-500 rounded-full"></div>
                            <span className="font-semibold text-white">Market Data Coverage</span>
                        </div>
                        <p className="text-gray-400 text-sm ml-6">
                            Number of price sources and market data points available
                        </p>
                    </div>
                    <div className="glass-card p-4 border-white/10">
                        <div className="flex items-center space-x-3 mb-2">
                            <div className="w-3 h-3 bg-gradient-to-r from-blue-400 to-blue-500 rounded-full"></div>
                            <span className="font-semibold text-white">Data Freshness</span>
                        </div>
                        <p className="text-gray-400 text-sm ml-6">
                            How recent the price and market information is
                        </p>
                    </div>
                    <div className="glass-card p-4 border-white/10">
                        <div className="flex items-center space-x-3 mb-2">
                            <div className="w-3 h-3 bg-gradient-to-r from-purple-400 to-purple-500 rounded-full"></div>
                            <span className="font-semibold text-white">Supplier Information</span>
                        </div>
                        <p className="text-gray-400 text-sm ml-6">
                            Availability of detailed supplier data and contact information
                        </p>
                    </div>
                    <div className="glass-card p-4 border-white/10">
                        <div className="flex items-center space-x-3 mb-2">
                            <div className="w-3 h-3 bg-gradient-to-r from-orange-400 to-orange-500 rounded-full"></div>
                            <span className="font-semibold text-white">Forecast Accuracy</span>
                        </div>
                        <p className="text-gray-400 text-sm ml-6">
                            Quality of historical data for price trend predictions
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default DataQualityReport;