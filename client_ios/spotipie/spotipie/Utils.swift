//
//  Utils.swift
//  spotipie
//
//  Created by Sudhip Nashi on 4/29/24.
//

import Foundation

func dateToString(date: Date) -> String {
    let dateFormatter = DateFormatter()
    dateFormatter.dateFormat = "MMM d, y HH:mm:ss"
    return dateFormatter.string(from: date)
}
