//
//  ReportView.swift
//  spotipie
//
//  Created by Sudhip Nashi on 04/08/24.
//

import SwiftUI

struct StatCell: View {
    @State var title: String
    @State var value: String
    
    var body: some View {
        HStack {
            Text(title)
            Spacer()
            Text(value)
        }
    }
}

struct ReportView: View {
    @State var report: Report
    @State var title: String
    
    var body: some View {
        NavigationStack {
            List {
                Section("Stats") {
                    let timeInterval = TimeInterval(report.stats.listening_time_ms/1000)
                    StatCell(title: "Avg. Scrobble/Day", value: String(report.stats.avg_scrobbles_per_day))
                    StatCell(title: "Listening Time", value: String(format: "%d hr %d min", timeInterval.hour, timeInterval.second))
                    StatCell(title: "Num. Artists", value: String(report.stats.num_artists))
                    StatCell(title: "Num. Albums", value: String(report.stats.num_albums))
                    StatCell(title: "Num. Tracks", value: String(report.stats.num_tracks))
                    
                }
                
                Section("Busiest Day") {
                    if let date = ISO8601DateFormatter().date(from: report.stats.highest_day.date) {
                        let dateFormatter = DateFormatter() 
                        StatCell(title: "Date", value: dateToString(date: date, time: false))
                        StatCell(title: "Play Count", value: String(report.stats.highest_day.play_count))
                    }
                }
                
                Section("Most Played Songs") {
                    ForEach(report.ten_most_played_tracks, id: \.id) { song in
                        NavigationLink {
                            SongDetailView(song: Song(id: song.id))
                        } label: {
                            GenericCell(name: song.name, image_url: song.cover_image_url, play_count: song.play_count)
                        }
                    }
                }
                
                Section("Most Played Albums") {
                    ForEach(report.ten_most_played_albums, id: \.id) { album in
                        NavigationLink {
                            AlbumDetailView(album: Album(id: album.id))
                        } label: {
                            GenericCell(name: album.name, image_url: album.cover_image_url, play_count: album.play_count)
                        }
                    }
                }
                
                Section("Most Played Artists") {
                    ForEach(report.ten_most_played_artists, id: \.id) { artist in
                        NavigationLink {
                            EmptyView()
                        } label: {
                            ArtistCell(name: artist.name, play_count: artist.play_count, id: artist.id)
                        }
                    }
                }
            }
            .animation(.snappy, value: report.id)
            .navigationTitle(title)
        }
    }
}
