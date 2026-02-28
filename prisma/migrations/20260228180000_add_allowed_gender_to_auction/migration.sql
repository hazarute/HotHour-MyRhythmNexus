-- CreateEnum
CREATE TYPE "public"."AllowedGender" AS ENUM ('FEMALE', 'MALE', 'ANY');

-- AlterTable
ALTER TABLE "public"."auctions"
ADD COLUMN "allowedGender" "public"."AllowedGender" NOT NULL DEFAULT 'ANY';
