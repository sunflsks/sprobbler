//
//  Top10Data.swift
//  spotipie
//
//  Created by Sudhip Nashi on 03/08/24.
//

import Foundation

struct Report : Decodable, Identifiable {
    enum times : String, CaseIterable {
        case week = "weekly"
        case month = "monthly"
        case year = "yearly"
        case allTime = "alltime"
        
        static func label(time: times) -> String {
            switch time {
            case week:
                return "Week"
            case month:
                return "Month"
            case year:
                return "Year"
            case allTime:
                return "All Time"
            }
            
        }
    }
    
    struct Stats: Decodable {
        struct HighestDayStats: Decodable {
            let date: Date
            let play_count: Int
        }
        
        struct AverageScrobbles: Decodable, Identifiable {
            let id = UUID()
            
            let start: Date
            let end: Date
            let count: Int
            
            private enum CodingKeys: String, CodingKey {
                case start
                case end
                case count
            }
        }
        
        struct GenreStats: Decodable {
            let genre: String
            let count: Int
            
            private enum CodingKeys: String, CodingKey {
                case genre
                case count
            }
        }
        
        let avg_scrobbles_per_day: Int
        let listening_time_ms: Int
        let num_artists: Int
        let num_albums: Int
        let num_tracks: Int
        let highest_day: HighestDayStats
        let averages: [AverageScrobbles]
        let genre_stats: [GenreStats]
    }

    private enum CodingKeys: String, CodingKey {
        case ten_most_played_artists
        case ten_most_played_albums
        case ten_most_played_tracks
        case report_type
        case stats
    }
    
    let id = UUID()
    var time: times? = nil
    
    let ten_most_played_artists: [PlayedItem]
    let ten_most_played_albums: [PlayedItem]
    let ten_most_played_tracks: [PlayedItem]
    let report_type: String
    let stats: Stats
    
    static func load(base_url: URL, time: times) async throws -> Report? {
        let (data, response) = try await URLSessionManager.normalSessionManager.data(from: URL(string: "/reports/" + time.rawValue, relativeTo: base_url) ?? URL(string: DEFAULT_URL)!)
        
        guard (response as? HTTPURLResponse)?.statusCode == 200 else {
            return nil
        }
        
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        var retVal = try decoder.decode(Report.self, from: data)
        retVal.time = time
        return retVal
    }
}
