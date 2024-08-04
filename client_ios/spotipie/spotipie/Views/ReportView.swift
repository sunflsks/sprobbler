//
//  ReportView.swift
//  spotipie
//
//  Created by Sudhip Nashi on 04/08/24.
//

import SwiftUI

struct ReportView: View {
    @State var report: Report
    @State var title: String
    
    var body: some View {
        NavigationStack {
            List {
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
            .navigationTitle(title)
        }
    }
}
