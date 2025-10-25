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
        <div className="bg-white rounded-lg shadow-md border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-xl font-semibold text-gray-900">Data Quality Report</h2>
            </div>

            <div className="px-6 py-4">
                {/* Overall Score */}
                <div className="mb-6">
                    <div className="flex items-center justify-between mb-3">
                        <h3 className="text-lg font-medium text-gray-900">Overall Data Quality</h3>
                        <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getScoreColor(report.overallScore)}`}>
                            {getScoreLabel(report.overallScore)} ({Math.round(report.overallScore * 100)}%)
                        </span>
                    </div>

                    <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                        <div
                            className={`h-2 rounded-full transition-all duration-300 ${report.overallScore >= 0.8 ? 'bg-green-500' :
                                report.overallScore >= 0.6 ? 'bg-yellow-500' : 'bg-red-500'
                                }`}
                            style={{ width: `${report.overallScore * 100}%` }}
                        ></div>
                    </div>

                    <p className="text-sm text-gray-600">
                        {getScoreDescription(report.overallScore)}
                    </p>
                </div>

                {/* Missing Data Sources */}
                {report.missingDataSources && report.missingDataSources.length > 0 && (
                    <div className="mb-6">
                        <h3 className="text-lg font-medium text-gray-900 mb-3">Missing Data Sources</h3>
                        <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
                            <div className="flex items-start space-x-3">
                                <div className="text-yellow-500 text-xl">⚠️</div>
                                <div>
                                    <h4 className="text-sm font-medium text-yellow-800 mb-2">
                                        Some data sources are unavailable
                                    </h4>
                                    <ul className="text-sm text-yellow-700 space-y-1">
                                        {report.missingDataSources.map((source, index) => (
                                            <li key={index} className="flex items-center space-x-2">
                                                <span className="w-1.5 h-1.5 bg-yellow-500 rounded-full"></span>
                                                <span>{source}</span>
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Recommendations */}
                {report.recommendations && report.recommendations.length > 0 && (
                    <div>
                        <h3 className="text-lg font-medium text-gray-900 mb-3">Data Quality Recommendations</h3>
                        <div className="space-y-3">
                            {report.recommendations.map((recommendation, index) => (
                                <div key={index} className="bg-blue-50 border border-blue-200 rounded-md p-3">
                                    <div className="flex items-start space-x-3">
                                        <div className="text-blue-500 text-lg">💡</div>
                                        <p className="text-sm text-blue-800">{recommendation}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Data Quality Legend */}
                <div className="mt-6 pt-6 border-t border-gray-200">
                    <h4 className="text-sm font-medium text-gray-900 mb-3">Data Quality Factors</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                        <div>
                            <div className="flex items-center space-x-2 mb-1">
                                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                                <span className="font-medium">Market Data Coverage</span>
                            </div>
                            <p className="text-gray-600 text-xs ml-4">
                                Number of price sources and market data points available
                            </p>
                        </div>
                        <div>
                            <div className="flex items-center space-x-2 mb-1">
                                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                                <span className="font-medium">Data Freshness</span>
                            </div>
                            <p className="text-gray-600 text-xs ml-4">
                                How recent the price and market information is
                            </p>
                        </div>
                        <div>
                            <div className="flex items-center space-x-2 mb-1">
                                <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                                <span className="font-medium">Supplier Information</span>
                            </div>
                            <p className="text-gray-600 text-xs ml-4">
                                Availability of detailed supplier data and contact information
                            </p>
                        </div>
                        <div>
                            <div className="flex items-center space-x-2 mb-1">
                                <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
                                <span className="font-medium">Forecast Accuracy</span>
                            </div>
                            <p className="text-gray-600 text-xs ml-4">
                                Quality of historical data for price trend predictions
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default DataQualityReport;