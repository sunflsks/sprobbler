//
//  Utils.swift
//  spotipie
//
//  Created by Sudhip Nashi on 4/29/24.
//

import Foundation

let DEFAULT_URL = "https://example.com" // some placeholder

struct URLSessionManager {
    static let cachedSessionManager: URLSession = {
        let configuration = URLSessionConfiguration.default
        configuration.requestCachePolicy = .returnCacheDataElseLoad
        return URLSession(configuration: configuration)
    }()
    
    static let normalSessionManager: URLSession = {
        return URLSession(configuration: .default)
    }()
}

func dateToString(date: Date) -> String {
    let dateFormatter = DateFormatter()
    dateFormatter.dateFormat = "MMM d, y HH:mm:ss"
    return dateFormatter.string(from: date)
}

func dateFromISO(str: String) -> Date? {
    let formatter = ISO8601DateFormatter()
    formatter.formatOptions = [.withFractionalSeconds, .withInternetDateTime]
    return formatter.date(from: str)
}

// https://stackoverflow.com/questions/30771820/how-to-convert-timeinterval-into-minutes-seconds-and-milliseconds-in-swift
extension TimeInterval {
    var hourMinuteSecondMS: String {
        String(format:"%d:%02d:%02d.%03d", hour, minute, second, millisecond)
    }
    var minuteSecond: String {
        String(format:"%d:%02d", minute, second)
    }
    var hour: Int {
        Int((self/3600).truncatingRemainder(dividingBy: 3600))
    }
    var minute: Int {
        Int((self/60).truncatingRemainder(dividingBy: 60))
    }
    var second: Int {
        Int(truncatingRemainder(dividingBy: 60))
    }
    var millisecond: Int {
        Int((self*1000).truncatingRemainder(dividingBy: 1000))
    }
}

extension String {
    func trim() -> String {
        return self.trimmingCharacters(in: .whitespacesAndNewlines)
    }
}
