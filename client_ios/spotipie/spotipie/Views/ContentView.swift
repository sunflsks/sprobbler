//
//  GlobalDataView.swift
//  spotipie
//
//  Created by Sudhip Nashi on 4/27/24.
//

import SwiftUI


struct ContentView: View {
    @State var globalData: GlobalData?
    
    func refreshData() async {
        globalData = try? await GlobalData.getGlobalData()
    }
    
    var body: some View {
        NavigationStack {
            List {
                Section(header: Text("Most Recent Scrobbles")) {
                    ForEach(globalData?.ten_most_recent_scrobbles ?? [], id: \.played_at) { song in
                        NavigationLink {
                            SongDetailView(song: Song(id: song.track_id))
                        } label: {
                            ScrobbleCell(name: song.name, played_at: dateFromISO(str: song.played_at), image_url: song.cover_image_url)
                        }
                    }
                    
                    NavigationLink {
                        ScrobblesByTimestampView(globalData: globalData)
                    } label: {
                        HStack {
                            Image(systemName: "music.note.list")
                                .resizable()
                                .scaledToFit()
                                .frame(width: 40, height: 40)
                                .cornerRadius(5)
                            
                            Text("Show More")
                        }
                    }
                }
                
                Section(header: Text("Most Played")) {
                    NavigationLink {
                        Top10ArtistView(globalData: globalData)
                    } label: {
                        HStack {
                            Image(systemName: "music.mic")
                                .resizable()
                                .scaledToFit()
                                .frame(width: 40, height: 40)
                                .cornerRadius(5)
                            
                            Text("Artists")
                        }
                    }
                    
                    NavigationLink {
                        Top10AlbumView(globalData: globalData)
                    } label: {
                        HStack {
                            Image(systemName: "person.2.crop.square.stack")
                                .resizable()
                                .scaledToFit()
                                .frame(width: 40, height: 40)
                                .cornerRadius(5)
                            
                            Text("Albums")
                        }
                    }
                    
                    NavigationLink {
                        Top10SongView(globalData: globalData)
                    } label: {
                        HStack {
                            Image(systemName: "music.quarternote.3")
                                .resizable()
                                .scaledToFit()
                                .frame(width: 40, height: 40)
                                .cornerRadius(5)
                            
                            Text("Tracks")
                        }
                    }
                }
            }
            .navigationTitle("Spotipie")
        }
        .task {
            await refreshData()
        }
        .refreshable {
            await refreshData()
        }
    }
}
