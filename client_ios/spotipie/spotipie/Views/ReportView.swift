//
//  ReportView.swift
//  spotipie
//
//  Created by Sudhip Nashi on 04/08/24.
//

import SwiftUI
import Charts

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
                    StatCell(title: "Listening Time", value: String(format: "%d min", report.stats.listening_time_ms / 1000 / 60))
                    StatCell(title: "Num. Artists", value: String(report.stats.num_artists))
                    StatCell(title: "Num. Albums", value: String(report.stats.num_albums))
                    StatCell(title: "Num. Tracks", value: String(report.stats.num_tracks))
                    
                }
                
                Section {
                    VStack {
                        HStack {
                            Text("Average Scrobbles / Day").font(.title2).fontWeight(.bold)
                            Spacer()
                        }
                        Chart {
                            let gradient = Gradient(colors: [.accentColor.opacity(0.8), .accentColor.opacity(0.1)])
                            ForEach(report.stats.averages) { avg in
                                let avgDate = Date.average(first: avg.start, second: avg.end)
                                LineMark(x: .value("Date", avgDate),
                                y: .value("Scrobbles", avg.count))
                                .interpolationMethod(.catmullRom)
                                .symbol(.circle)

                                AreaMark(x: .value("Date", avgDate),
                                y: .value("Scrobbles", avg.count))
                                .foregroundStyle(gradient)
                                .interpolationMethod(.catmullRom)
                            }
                        }
                        .padding(.bottom, 20)
                    }
                }
                
                Section(footer: Text("Predicted and presented all in-house :)")) {
                    VStack {
                        HStack {
                                Text("Genres").font(.title2).fontWeight(.bold)
                                Spacer()
                            }
                            Chart {
                                ForEach(report.stats.genre_stats, id: \.genre) { genre in
                                    SectorMark(
                                        angle: .value (
                                            "Count",
                                            genre.count
                                        ),
                                        innerRadius: .ratio(0.6),
                                        angularInset: 5
                                    ).foregroundStyle(
                                        by: .value(
                                            "Genre",
                                            genre.genre
                                        )
                                    )
                                }
                            }
                            .padding(.bottom, 20)
                            .scaledToFit()
                        }
                }
                
                Section("Busiest Day") {
                    StatCell(title: "Date", value: dateToString(date: report.stats.highest_day.date, time: false))
                    StatCell(title: "Play Count", value: String(report.stats.highest_day.play_count))
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
